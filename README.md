# 🕵️‍♂️ Risk Assessment AI Agent

> **An autonomous "ReAct" agent that researches companies, navigates complex websites, and generates comprehensive risk assessment reports in real-time.**

![Project Banner](https://via.placeholder.com/1200x400?text=Risk+Assessment+AI+Agent)

## 🚀 Overview

This project is a **full-stack AI application** designed to automate the due diligence process. It uses a **LangGraph-based ReAct Agent** (Reasoning + Acting) to autonomously browse the web, overcome obstacles (like popups and login walls), and synthesize data into professional risk reports.

Unlike standard scrapers, this agent **"sees"** the page using a headless browser (Playwright) and makes dynamic decisions based on what it encounters. You can watch it think and act via a **Live Agent Preview** that streams the browser view and internal logs to the frontend.

## ✨ Key Features

-   **🧠 Autonomous ReAct Agent**: Uses `LangGraph` and `Google Gemini 2.0 Flash` to reason, plan, and execute research tasks.
-   **👀 Live Agent Preview**: Watch the agent's "brain" at work with a real-time video feed of the headless browser and a streaming log of its thoughts.
-   **🛡️ Intelligent Navigation**:
    -   **Popup Killer**: Automatically detects and closes modals, cookie banners, and login walls (including LinkedIn).
    -   **Human Verification**: Detects and clicks "Verify you are human" checkboxes.
    -   **Deep Scouting**: Proactively finds "Team", "About", and "Investors" pages to gather deep context.
-   **⚡ High-Performance Architecture**:
    -   **Backend**: FastAPI with asynchronous event streaming (SSE).
    -   **Frontend**: Next.js 14 (App Router) with Tailwind CSS and Framer Motion.
    -   **Browsing**: Playwright with stealth plugins to avoid bot detection.

## 🛠️ Tech Stack

### Backend
-   **Python 3.10+**
-   **FastAPI**: High-performance async API framework.
-   **LangGraph**: For building stateful, multi-step agent workflows.
-   **LangChain**: For tool abstraction and LLM integration.
-   **Playwright**: For headless browser automation.
-   **Google Gemini**: The LLM "brain" powering the agent.

### Frontend
-   **Next.js 14**: React framework with Server Components.
-   **TypeScript**: For type-safe development.
-   **Tailwind CSS**: For modern, responsive styling.
-   **Framer Motion**: For smooth UI animations and transitions.
-   **Lucide React**: For beautiful icons.

## 📦 Installation & Setup

### Prerequisites
-   **Node.js** (v18+)
-   **Python** (v3.10+)
-   **Google Cloud API Key** (with Gemini API enabled)
-   **Google Custom Search Engine (CSE) ID**

### Quick Start (Windows)

We have provided a **one-click setup script** for Windows users.

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/risk-assessment-generator.git
    cd risk-assessment-generator
    ```

2.  **Configure Environment**:
    -   Rename `backend/.env.example` to `backend/.env`.
    -   Add your API keys:
        ```env
        GOOGLE_API_KEY=your_gemini_api_key
        GOOGLE_CSE_ID=your_search_engine_id
        ```

3.  **Run the Installer**:
    -   Double-click `setup_and_run.bat` OR run it from the terminal:
        ```cmd
        setup_and_run.bat
        ```
    -   This script will:
        -   Create a Python virtual environment.
        -   Install all backend dependencies (including Playwright browsers).
        -   Install all frontend dependencies.
        -   Start both the Backend (Port 8000) and Frontend (Port 3000).

4.  **Access the App**:
    -   Open `http://localhost:3000` in your browser.

### Manual Setup

<details>
<summary>Click to expand manual instructions</summary>

#### Backend
```bash
cd backend
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
playwright install
uvicorn main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```
</details>

## 🎮 Usage

1.  **Enter a Company Name**: On the homepage, type the name of the company you want to analyze (e.g., "Anthropic", "OpenAI").
2.  **Watch the Agent**: The "Live Preview" dashboard will appear.
    -   **Left Panel**: Real-time video feed of the agent browsing the web.
    -   **Right Panel**: Live logs showing the agent's reasoning ("Thinking...", "Clicking...", "Reading...").
3.  **View the Report**: Once the research is complete, a comprehensive Risk Assessment Report will be generated, covering:
    -   Company Overview
    -   Key Risks (Operational, Financial, Reputational)
    -   Market Position
    -   Final Risk Score

## 🔮 Future Roadmap

-   [ ] **Bright Data Integration**: Add support for residential proxies to scrape highly protected sites.
-   [ ] **PDF Export**: Download the risk report as a formatted PDF.
-   [ ] **Multi-Agent Collaboration**: Split the workload between a "Researcher", "Analyst", and "Critic" agent.
-   [ ] **History & Storage**: Save past reports to a database.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.
