@echo off
echo 🚀 Setting up Scientific Text Annotator Backend...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.11+ and add it to your PATH
    pause
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment
echo 🔧 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📦 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo ⚙️ Creating .env file...
    copy .env.example .env
    echo ⚠️ Please update the .env file with your actual configuration values
)

REM Create uploads directory
if not exist uploads mkdir uploads

echo ✅ Backend setup complete!
echo.
echo Next steps:
echo 1. Update .env file with your database and API keys
echo 2. Set up PostgreSQL database
echo 3. Run migrations: alembic upgrade head
echo 4. Start the server: uvicorn main:app --reload
echo.
echo Or use Docker Compose:
echo 1. Update .env file
echo 2. Run: docker-compose up -d

pause
