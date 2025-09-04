#!/usr/bin/env python3
"""
Development Cleanup Script for WIZARD-2.1

This script performs a complete cleanup for development:
- Clears logs
- Clears cache
- Clears temporary files
- Optionally reinstalls dependencies
"""

import os
import sys
import argparse
from pathlib import Path
import subprocess


def clear_logs():
    """
    Clear all log files.
    """
    print("🧹 Clearing logs...")
    project_root = Path(__file__).parent.parent
    logs_dir = project_root / "logs"
    
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        for log_file in log_files:
            log_file.unlink()
        print(f"✅ Deleted {len(log_files)} log file(s)")
    else:
        print("✅ No logs directory found")


def clear_cache():
    """
    Clear all cache files.
    """
    print("🧹 Clearing cache...")
    project_root = Path(__file__).parent.parent
    
    # Clear __pycache__ directories
    pycache_dirs = list(project_root.rglob("__pycache__"))
    for pycache_dir in pycache_dirs:
        if pycache_dir.is_dir():
            import shutil
            shutil.rmtree(pycache_dir)
    
    # Clear .pyc files
    pyc_files = list(project_root.rglob("*.pyc"))
    for pyc_file in pyc_files:
        pyc_file.unlink()
    
    # Clear build directories
    build_dirs = ["build", "dist", ".pytest_cache", ".mypy_cache"]
    for build_dir in build_dirs:
        build_path = project_root / build_dir
        if build_path.exists():
            import shutil
            shutil.rmtree(build_path)
    
    print(f"✅ Cleared {len(pycache_dirs)} __pycache__ directories")
    print(f"✅ Cleared {len(pyc_files)} .pyc files")


def clear_temp_files():
    """
    Clear temporary files.
    """
    print("🧹 Clearing temporary files...")
    project_root = Path(__file__).parent.parent
    
    # Clear OS specific temp files
    temp_files = [".DS_Store", "Thumbs.db", ".coverage"]
    cleared_count = 0
    
    for temp_file in temp_files:
        temp_paths = list(project_root.rglob(temp_file))
        for temp_path in temp_paths:
            if temp_path.is_file():
                temp_path.unlink()
                cleared_count += 1
    
    print(f"✅ Cleared {cleared_count} temporary file(s)")


def reinstall_dependencies():
    """
    Reinstall dependencies.
    """
    print("📦 Reinstalling dependencies...")
    project_root = Path(__file__).parent.parent
    venv_path = project_root / "venv"
    
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        return False
    
    if os.name == 'nt':  # Windows
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # Unix/Linux/macOS
        pip_exe = venv_path / "bin" / "pip"
    
    try:
        # Uninstall and reinstall
        subprocess.run([str(pip_exe), "uninstall", "-y", "-r", "requirements.txt"], 
                      cwd=project_root, capture_output=True)
        subprocess.run([str(pip_exe), "install", "-r", "requirements.txt"], 
                      cwd=project_root, check=True)
        print("✅ Dependencies reinstalled successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error reinstalling dependencies: {e}")
        return False


def main():
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description="WIZARD-2.1 Development Cleanup Script")
    parser.add_argument("--logs", action="store_true", help="Clear log files")
    parser.add_argument("--cache", action="store_true", help="Clear cache files")
    parser.add_argument("--temp", action="store_true", help="Clear temporary files")
    parser.add_argument("--deps", action="store_true", help="Reinstall dependencies")
    parser.add_argument("--all", action="store_true", help="Perform all cleanup operations")
    
    args = parser.parse_args()
    
    print("🧹 WIZARD-2.1 - Development Cleanup Script")
    print("=" * 50)
    
    if args.all or not any([args.logs, args.cache, args.temp, args.deps]):
        # If no specific flags or --all, do everything except deps
        clear_logs()
        clear_cache()
        clear_temp_files()
    else:
        if args.logs:
            clear_logs()
        if args.cache:
            clear_cache()
        if args.temp:
            clear_temp_files()
        if args.deps:
            reinstall_dependencies()
    
    print("\n🎉 Cleanup completed successfully!")


if __name__ == "__main__":
    main()
