@echo off
echo Setting up Risk Assessment Generator...

echo.
echo --- Backend Setup ---
cd backend
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)
call venv\Scripts\activate
echo Installing backend dependencies...
pip install -r requirements.txt
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo PLEASE EDIT backend/.env WITH YOUR API KEYS!
    pause
)

echo.
echo --- Frontend Setup ---
cd ..\frontend
echo Installing frontend dependencies...
call npm install

echo.
echo --- Starting Services ---
start "Backend API" cmd /k "cd ..\backend && venv\Scripts\activate && uvicorn main:app --reload"
start "Frontend App" cmd /k "npm run dev"

echo.
echo Application starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
pause
