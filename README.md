# RAG-LLM Testing Web App

This project is a web application for testing Retrieval-Augmented Generation (RAG) models with a user-friendly interface. It consists of a **backend** powered by Python's FastAPI framework and a **frontend** built using React.

---

## Table of Contents
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Setting Up Python Environment](#setting-up-python-environment)
- [Starting the Backend](#starting-the-backend)
- [Starting the Frontend](#starting-the-frontend)
- [Backend API Documentation](#backend-api-documentation)
  - [Endpoint: `/ask`](#route-ask)
- [Project Structure](#project-structure)
- [License](#license)

---

## Getting Started

### Prerequisites
Before starting, ensure you have the following installed:

#### For Backend:
- **Python**: Version 3.12.2 (or install using `pyenv`).
- **pyenv**: Ensure it is installed and properly configured.

#### For Frontend:
- **Node.js**: Version 20.11.0 or higher.
- **npm**: Comes with Node.js.

---

## Installation

### Clone the Repository
```bash
git clone https://github.com/your-repo/rag-llm-testing-web-app.git
cd rag-llm-testing-web-app
```

---

## Setting Up Python Environment

1. **Check if `pyenv` is Installed**
   - Run the following command:
     ```bash
     pyenv --version
     ```
   - If `pyenv` is not installed, you can install it using the following commands:

     **For Linux/macOS:**
     ```bash
     curl https://pyenv.run | bash
     ```

     After installation, add the following to your shell configuration file (`~/.bashrc` or `~/.zshrc`):
     ```bash
     export PATH="$HOME/.pyenv/bin:$PATH"
     eval "$(pyenv init --path)"
     eval "$(pyenv virtualenv-init -)"
     ```
     Reload your shell:
     ```bash
     source ~/.bashrc  # or ~/.zshrc
     ```

     **For Windows:**  
     Use [pyenv-win](https://github.com/pyenv-win/pyenv-win) by following their installation guide.

---

## Starting the Backend

1. **Navigate to the Backend Directory**  
   ```bash
   cd backend
   ```

2. **Set Up Python Environment**
   - Ensure Python 3.12.2 is available; install if necessary:
     ```bash
     pyenv install 3.12.2
     ```
   - Create and activate a virtual environment:
     ```bash
     pyenv virtualenv 3.12.2 venv
     pyenv activate venv
     ```

3. **Install Dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   - Copy the sample `.env` file:
     ```bash
     cp .env.sample .env
     ```
   - Fill in the API keys in the `.env` file:
     - Get `GOOGLE_API_KEY` from [Google AI Studio](https://aistudio.google.com/app/apikey).
     - Get `GROQ_API_KEY` from [Groq Console](https://console.groq.com/keys).

5. **(Optional) Customize Word Documents for RAG**
   - The `word_docs` folder contains some default Word documents used for the RAG model.
   - If you want to update the content or add new documents, replace or add files in the `word_docs` folder.
   - **Note:** Whenever the documents are updated, you must regenerate the embeddings.

6. **Generate Embeddings**  
   ```bash
   python generate_embeddings.py
   ```

7. **Start the Backend Server**  
   ```bash
   uvicorn main_with_history:app --host 0.0.0.0 --port 8080 --reload
   ```

   The backend will be available at [http://127.0.0.1:8080](http://127.0.0.1:8080).

---

## Starting the Frontend

1. **Navigate to the Frontend Directory**  
   ```bash
   cd frontend
   ```

2. **Verify Node.js Installation**  
   Check if Node.js is installed and meets the version requirement:
   ```bash
   node --version
   ```

3. **Install Dependencies**  
   ```bash
   npm install
   ```

4. **Update Backend URL**  
   Open `frontend/src/config.ts` and update the `BACKEND_URL` variable to point to your local backend:
   ```typescript
   export const BACKEND_URL = "http://127.0.0.1:8080";
   ```

5. **Start the Frontend Server**  
   ```bash
   npm run dev
   ```

   The frontend will be available at [http://localhost:5173](http://localhost:5173).

---

## Backend API Documentation

### Endpoint: `/ask`

#### Description
This endpoint allows users to send a question and chat history to retrieve answers along with related documents.

#### Request
- **Method:** `POST`
- **Content Type:** `application/json`

#### Sample Request Body
```json
{
    "question": "How many articles are there in this course?",
    "chat_history": [
        {"role": "human", "content": "How many downloadable resources does 'Selenium Webdriver with PYTHON from Scratch + Frameworks' course have?"},
        {"role": "system", "content": "9"}
    ]
}
```

#### Response
**Success**
- **Status Code:** `200`
- **Sample Response:**
    ```json
    {
        "answer": "23",
        "retrieved_docs": [
            {
                "file_name": "Selenium Webdriver with PYTHON from Scratch + Frameworks.docx",
                "page_content": "Complete Understanding on Selenium Python API Methods with real time Scenarios on LIVE Websites\n\"Last but not least\" you can clear any Interview and can Lead Entire Selenium Python Projects from Design Stage\nThis course includes:\n17.5 hours on-demand video\nAssignments\n23 articles\n9 downloadable resources\nAccess on mobile and TV\nCertificate of completion\nRequirements"
            }
        ]
    }
    ```

**Failure**
- **Status Codes:** `400`, `422`, `500`
- **Sample Error Response:**
    ```json
    {
        "detail": [
            {
                "type": "missing",
                "loc": [
                    "body",
                    "chat_history"
                ],
                "msg": "Field required",
                "input": {
                    "question": "How many articles are there in this course?"
                }
            }
        ]
    }
    ```

---

## Project Structure

```plaintext
rag-llm-testing-web-app/
├── backend/
│   ├── main_with_history.py       # FastAPI app
│   ├── generate_embeddings.py     # Script to generate embeddings
│   ├── requirements.txt           # Python dependencies
│   ├── word_docs/                 # Folder containing Word documents for RAG model
│   └── .env.sample                # Sample environment variables
├── frontend/
│   ├── src/
│   │   ├── config.ts              # Frontend configuration
│   │   └── ...                    # React components and utilities
│   └── package.json               # Node.js dependencies
└── README.md                      # Project documentation
```

---

## License
This project is licensed under the [MIT License](LICENSE).

---

Enjoy Testing with RAG-LLM Testing Web App! 🚀