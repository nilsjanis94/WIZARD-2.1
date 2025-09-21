@echo off
REM WIZARD-2.1 Windows Testing Script (Batch Version)
REM Simple batch script for Windows users who prefer cmd.exe

echo [INFO] Starting WIZARD-2.1 Windows testing...

REM Change to project root (assuming script is in scripts/ subdirectory)
cd /d "%~dp0.."

echo [INFO] Working directory: %CD%

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    python3 --version >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Python not found. Please install Python 3.13+
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

echo [INFO] Using: %PYTHON_CMD%

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo [INFO] Creating virtual environment...
    %PYTHON_CMD% -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [INFO] Upgrading pip...
%PYTHON_CMD% -m pip install --upgrade pip

REM Install requirements
echo [INFO] Installing requirements...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install requirements
    pause
    exit /b 1
)

REM Install dev requirements (optional)
pip install -r requirements-dev.txt
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Failed to install dev requirements, continuing...
)

REM Install project
echo [INFO] Installing project...
pip install -e .
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install project
    pause
    exit /b 1
)

REM Run basic tests
echo [INFO] Running basic import test...
%PYTHON_CMD% -c "import sys; sys.path.insert(0, 'src'); from wizard_2_1.main import main; print('✓ Main module imports successfully')"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Import test failed
    pause
    exit /b 1
)

REM Test UI components
echo [INFO] Testing UI components...
%PYTHON_CMD% -c "import sys; sys.path.insert(0, 'src'); import os; os.environ['QT_QPA_PLATFORM'] = 'offscreen'; from PyQt6.QtWidgets import QApplication; from services.ui_service import UIService; app = QApplication([]); ui_service = UIService(); print(f'✓ UI service initialized, platform: {ui_service.current_platform}'); app.quit()"
if %ERRORLEVEL% neq 0 (
    echo [WARNING] UI test failed, but continuing...
)

echo [SUCCESS] Windows testing setup completed!
echo.
echo Next steps:
echo 1. Start the application: venv\Scripts\python scripts\start_app.py
echo 2. Test the UI manually
echo 3. Check logs in logs\ directory for any errors
echo.
pause
