@echo off
setlocal enabledelayedexpansion

echo.
echo TaskBot Environment Setup
echo ============================
echo.

set /p GROQ_KEY="Enter your Groq API key: "

REM Create .env file with UTF-8 encoding
(
    echo GROQ_API_KEY=!GROQ_KEY!
) > .env

echo.
echo ✓ .env file created!
echo.
echo Now activate venv and run:
echo   venv\Scripts\activate
echo   python main.py
echo.
pause