#!/usr/bin/env python3
"""
Start Application Script for WIZARD-2.1

This script starts the WIZARD-2.1 application with proper environment setup.
"""

import os
import sys
import subprocess
from pathlib import Path

# Global variable for verbose output
verbose = False


def check_venv():
    """
    Check if virtual environment is activated.
    
    Returns:
        bool: True if venv is activated
    """
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)


def activate_venv():
    """
    Try to activate virtual environment.
    
    Returns:
        bool: True if venv was activated successfully
    """
    project_root = Path(__file__).parent.parent
    venv_path = project_root / "venv"
    
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("   Please run: python -m venv venv")
        return False

    # Try to activate venv
    if os.name == 'nt':  # Windows
        activate_script = venv_path / "Scripts" / "activate.bat"
        python_exe = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        activate_script = venv_path / "bin" / "activate"
        python_exe = venv_path / "bin" / "python"

    if not python_exe.exists():
        print("❌ Python executable not found in virtual environment!")
        return False
    
    return True


def install_dependencies():
    """
    Install dependencies if needed.

    Returns:
        bool: True if dependencies are installed
    """
    project_root = Path(__file__).parent.parent
    venv_path = project_root / "venv"

    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # Unix/Linux/macOS
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"

    try:
        # Check if requirements are installed
        result = subprocess.run([
            str(python_exe), "-c", 
            "import PyQt6; import pandas; import numpy; import matplotlib"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print("📦 Installing dependencies...")
            subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"],
                         cwd=project_root, check=True, capture_output=not verbose)
            if verbose:
                print("✅ Dependencies installed successfully!")
        else:
            if verbose:
                print("✅ Dependencies are already installed")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def start_application():
    """
    Start the WIZARD-2.1 application.

    Returns:
        bool: True if application started successfully
    """
    project_root = Path(__file__).parent.parent
    venv_path = project_root / "venv"

    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/macOS
        python_exe = venv_path / "bin" / "python"

    try:
        # Quiet startup - logs go to files only
        result = subprocess.run([str(python_exe), "-m", "src.main"], cwd=project_root)

        # Only show errors
        if result.returncode != 0:
            print(f"❌ Application exited with error code: {result.returncode}")

        return result.returncode == 0

    except KeyboardInterrupt:
        print("\n⏹️  Application stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False


def main():
    """
    Main function.
    """
    # Minimal output - only show warnings and errors
    global verbose
    verbose = os.environ.get('WIZARD_VERBOSE', '').lower() in ('true', '1', 'yes')

    if verbose:
        print("🚀 WIZARD-2.1 - Start Application Script")
        print("=" * 50)

    # Check if we're in a virtual environment
    if not check_venv():
        print("⚠️  Virtual environment not activated!")
        print("   Attempting to use project venv...")

        if not activate_venv():
            print("❌ Failed to activate virtual environment!")
            print("   Please run: source venv/bin/activate (Unix/macOS)")
            print("   or: venv\\Scripts\\activate (Windows)")
            sys.exit(1)

    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies!")
        sys.exit(1)

    # Start application
    if not start_application():
        print("❌ Failed to start application!")
        sys.exit(1)

    if verbose:
        print("\n🎉 Application session completed!")


if __name__ == "__main__":
    main()
