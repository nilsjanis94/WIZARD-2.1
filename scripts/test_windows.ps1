# WIZARD-2.1 Windows Testing Script
# PowerShell script for testing on Windows

param(
    [switch]$SkipTests,
    [switch]$SkipBuild,
    [switch]$Clean
)

# Colors for output
$Green = "Green"
$Red = "Red"
$Yellow = "Yellow"
$Blue = "Blue"
$NC = "White" # Default

function Write-ColoredOutput {
    param([string]$Color, [string]$Message)
    Write-Host $Message -ForegroundColor $Color
}

function Write-Status { param([string]$Message) Write-ColoredOutput $Blue "[INFO] $Message" }
function Write-Success { param([string]$Message) Write-ColoredOutput $Green "[SUCCESS] $Message" }
function Write-Warning { param([string]$Message) Write-ColoredOutput $Yellow "[WARNING] $Message" }
function Write-Error { param([string]$Message) Write-ColoredOutput $Red "[ERROR] $Message" }

# Check if running on Windows
if ($PSVersionTable.Platform -ne "Win32NT" -and -not $IsWindows) {
    Write-Error "This script is designed for Windows PowerShell"
    exit 1
}

# Project root directory
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $PSCommandPath)
Set-Location $ProjectRoot

Write-Status "Starting WIZARD-2.1 Windows testing in: $ProjectRoot"

# Clean if requested
if ($Clean) {
    Write-Status "Cleaning Python cache files..."
    Get-ChildItem -Path . -Recurse -Include "__pycache__", "*.pyc", "*.pyo" -Force | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path "build") { Remove-Item "build" -Recurse -Force }
    if (Test-Path "dist") { Remove-Item "dist" -Recurse -Force }
    Write-Success "Cleanup completed"
}

# Check Python version
$pythonVersion = python --version 2>$null
if ($LASTEXITCODE -ne 0) {
    $pythonVersion = python3 --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Python not found. Please install Python 3.13+"
        exit 1
    }
}
Write-Status "Using: $pythonVersion"

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Status "Creating virtual environment..."
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment"
        exit 1
    }
}

# Activate virtual environment
Write-Status "Activating virtual environment..."
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Status "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
Write-Status "Installing dependencies..."
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install requirements"
    exit 1
}

pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Failed to install dev requirements, continuing..."
}

# Install project in development mode
if (-not $SkipBuild) {
    Write-Status "Installing project in development mode..."
    pip install -e .
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install project"
        exit 1
    }
}

# Run tests
if (-not $SkipTests) {
    Write-Status "Running tests..."

    # Basic import test
    Write-Status "Testing basic imports..."
    python -c "import sys; sys.path.insert(0, 'src'); from wizard_2_1.main import main; print('✓ Main module imports successfully')"

    # Run pytest
    Write-Status "Running pytest..."
    pytest tests/ -v --tb=short
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Some tests failed, but continuing..."
    } else {
        Write-Success "All tests passed!"
    }
}

# Test UI components (basic smoke test)
Write-Status "Testing UI components..."
python -c "
import sys
sys.path.insert(0, 'src')
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer
    import os
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # Headless mode

    app = QApplication([])
    print('✓ PyQt6 imports and initializes successfully')

    # Test our UI service
    from services.ui_service import UIService
    ui_service = UIService()
    print(f'✓ UI service initialized, platform: {ui_service.current_platform}')

    app.quit()
    print('✓ UI components test completed successfully')

except Exception as e:
    print(f'✗ UI test failed: {e}')
    sys.exit(1)
"

Write-Success "Windows testing completed!"

# Instructions for manual testing
Write-Status @"

Manual Testing Instructions:
---------------------------

1. Start the application:
   venv\Scripts\python scripts\start_app.py

2. Test the UI:
   - Check if all text is visible (black text on colored backgrounds)
   - Test comboboxes (Y1, Y2, X axis selectors)
   - Verify buttons and labels are readable

3. Test functionality:
   - Try opening a .tob file
   - Test axis controls
   - Verify plot rendering

4. Check logs in logs\ directory for any errors

Known Windows-specific considerations:
- Qt may use different default fonts than macOS
- Window decorations might look different
- File dialog behavior may vary

"@
