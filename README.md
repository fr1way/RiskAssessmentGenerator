# Risk Assessment Generator

A full-stack AI application that performs detailed risk assessments on companies using Gemini and Google Search.

## Prerequisites

- Node.js & npm
- Python 3.8+
- Google Cloud API Key (with Gemini and Custom Search API enabled)
- Google Custom Search Engine (CSE) ID

## Setup

1.  **Backend Setup**:
    ```bash
    cd backend
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env
    # Edit .env and add your GOOGLE_API_KEY and GOOGLE_CSE_ID
    ```

2.  **Frontend Setup**:
    ```bash
    cd frontend
    npm install
    ```

## Running the App

1.  **Start Backend**:
    ```bash
    cd backend
    .\venv\Scripts\activate
    uvicorn main:app --reload
    ```

2.  **Start Frontend**:
    ```bash
    cd frontend
    npm run dev
    ```

3.  Open [http://localhost:3000](http://localhost:3000) in your browser.

## Architecture

- **Frontend**: Next.js, Tailwind CSS, Framer Motion.
- **Backend**: FastAPI, LangChain, Google Gemini.
