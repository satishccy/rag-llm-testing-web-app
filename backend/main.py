from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings


# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
# Initialize vector store and LLM
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,  # Embeddings are already persisted
    persist_directory="./chroma_langchain_db",
)

llm = ChatGroq(model="gemma2-9b-it")

# Request model
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    question = request.question

    # Retrieve relevant documents
    retriever = vector_store.as_retriever(k=3)
    retrieved_docs = retriever.invoke(question)

    if not retrieved_docs:
        raise HTTPException(status_code=404, detail="No relevant documents found.")

    # Build context from retrieved documents
    context = "\n".join([result.page_content for result in retrieved_docs])

    # Create the prompt for LLM
    prompt = f"""Answer the question in detail based on the following context only: 
    {context} 
    Guidelines for answering:
    1. Do not refer to any external sources.
    2. Do not provide any irrelevant information.
    3. No need to start with text like 'based on the context provided' or 'according to the context'.

    Question: {question}"""

    print(prompt)

    # Generate the answer using LLM
    answer = llm.invoke(prompt)
    answer_text = answer.content

    # Response with metadata
    response = {
        "answer": answer_text,
        "retrieved_documents": [
            {"file_name": result.metadata["file_name"], "content": result.page_content}
            for result in retrieved_docs
        ],
    }
    return response
