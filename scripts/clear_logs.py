#!/usr/bin/env python3
"""
Clear Logs Script for WIZARD-2.1

This script clears all log files from the logs directory.
"""

import os
import sys
from pathlib import Path
import shutil


def clear_logs():
    """
    Clear all log files from the logs directory.
    """
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    logs_dir = project_root / "logs"
    
    if not logs_dir.exists():
        print("❌ Logs directory does not exist")
        return False
    
    # Count log files before deletion
    log_files = list(logs_dir.glob("*.log"))
    log_count = len(log_files)
    
    if log_count == 0:
        print("✅ No log files found to delete")
        return True
    
    try:
        # Delete all log files
        for log_file in log_files:
            log_file.unlink()
            print(f"🗑️  Deleted: {log_file.name}")
        
        print(f"✅ Successfully deleted {log_count} log file(s)")
        return True
        
    except Exception as e:
        print(f"❌ Error deleting log files: {e}")
        return False


def main():
    """
    Main function.
    """
    print("🧹 WIZARD-2.1 - Clear Logs Script")
    print("=" * 40)
    
    success = clear_logs()
    
    if success:
        print("\n🎉 Log clearing completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Log clearing failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
