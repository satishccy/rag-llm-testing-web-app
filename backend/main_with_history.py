from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, field_validator
from typing import List, Dict
from langchain_core.messages.chat import ChatMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.runnables.history import RunnableWithMessageHistory,ConfigurableFieldSpec
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from fastapi.middleware.cors import CORSMiddleware
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()

import os
required_env_vars = [
    "GOOGLE_API_KEY",
    "GROQ_API_KEY"
]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

word_docs_folder = 'word_docs'

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

llm = ChatGroq(model="gemma2-9b-it")


vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",
)

retriever_prompt = (
    """Given a chat history and the latest user question which might reference context in the chat history,
    formulate a standalone question which can be understood without the chat history.
    Do NOT answer the question, just reformulate it if needed and otherwise return it as is."""
)
    
contextualize_q_prompt  = ChatPromptTemplate.from_messages(
    [
        ("system", retriever_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

retriever = vector_store.as_retriever(k=3)

history_aware_retriever = create_history_aware_retriever(llm ,retriever, contextualize_q_prompt)

system_prompt = (
    """You are a helpful assistant. Answer questions with detailed and accurate information strictly based on the given context.
    Ensure your responses are concise, relevant, and do not include any references to external sources or unnecessary details.
    Avoid introductory phrases like "Based on the context provided

    Context:{context}"""
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

def get_session_history(last_messages: InMemoryChatMessageHistory) -> InMemoryChatMessageHistory:
    return last_messages

# Conversational RAG Chain initialization (exportable variable)
conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
    history_factory_config=[
        ConfigurableFieldSpec(
            id="last_messages",
            annotation=InMemoryChatMessageHistory,
            name="Last Messages",
            description="Last messages in the chat history.",
            default=[],
            is_shared=True,
        )
    ],
)

# FastAPI app initialization
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class AskRequest(BaseModel):
    question: str
    chat_history: List[Dict[str, str]]

    # Add validation
    class Config:
        min_length_question = 1
        max_length_question = 1000

    @field_validator('question')
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty')
        if len(v) > cls.Config.max_length_question:
            raise ValueError(f'Question must be less than {cls.Config.max_length_question} characters')
        return v

@app.post("/ask")
async def ask_question(request: AskRequest):
    try:
        session_id = str(uuid4())
        # Prepare chat history in the required format
        chat_history = [
            HumanMessage(message["content"]) if message["role"]=="human" else AIMessage(message["content"])
            for message in request.chat_history
        ]

        base_chat_history = ChatMessageHistory(messages=chat_history[-5:])

        # Invoke the RAG chain with the input question and chat history
        response = conversational_rag_chain.invoke(
            {"input": request.question, "chat_history": chat_history},
            {'configurable': {'last_messages': base_chat_history,'session_id': session_id}}
        )

        # Extract retrieved documents and answer
        retrieved_docs = response["context"]
        answer = response["answer"]

        # Format retrieved document metadata
        docs_metadata = [
            {"file_name": doc.metadata["file_name"], "page_content": doc.page_content}
            for doc in retrieved_docs
        ]

        return {"answer": answer, "retrieved_docs": docs_metadata}

    except Exception as e:
        if isinstance(e, ValueError):
            raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
        print(e)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Export conversational_rag_chain for testing
__all__ = ["conversational_rag_chain"]
