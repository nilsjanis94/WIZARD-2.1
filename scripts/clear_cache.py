#!/usr/bin/env python3
"""
Clear Cache Script for WIZARD-2.1

This script clears all cache files and temporary data.
"""

import os
import sys
from pathlib import Path
import shutil


def clear_cache():
    """
    Clear all cache files and temporary data.
    """
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Define cache directories and files to clear
    cache_items = [
        # Python cache
        project_root / "__pycache__",
        project_root / "src" / "__pycache__",
        project_root / "src" / "models" / "__pycache__",
        project_root / "src" / "views" / "__pycache__",
        project_root / "src" / "controllers" / "__pycache__",
        project_root / "src" / "services" / "__pycache__",
        project_root / "src" / "utils" / "__pycache__",
        project_root / "src" / "exceptions" / "__pycache__",
        project_root / "src" / "views" / "dialogs" / "__pycache__",
        project_root / "tests" / "__pycache__",
        project_root / "tests" / "unit" / "__pycache__",
        project_root / "tests" / "integration" / "__pycache__",
        project_root / "tests" / "ui" / "__pycache__",
        
        # Build directories
        project_root / "build",
        project_root / "dist",
        
        # IDE and editor files
        project_root / ".pytest_cache",
        project_root / ".mypy_cache",
        project_root / ".coverage",
        project_root / "htmlcov",
        
        # OS specific
        project_root / ".DS_Store",
        project_root / "Thumbs.db",
    ]
    
    deleted_count = 0
    
    for item in cache_items:
        if item.exists():
            try:
                if item.is_dir():
                    shutil.rmtree(item)
                    print(f"🗑️  Deleted directory: {item.name}")
                else:
                    item.unlink()
                    print(f"🗑️  Deleted file: {item.name}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error deleting {item}: {e}")
    
    # Clear Python bytecode files recursively
    try:
        for pycache_dir in project_root.rglob("__pycache__"):
            if pycache_dir.is_dir():
                shutil.rmtree(pycache_dir)
                print(f"🗑️  Deleted __pycache__: {pycache_dir.relative_to(project_root)}")
                deleted_count += 1
    except Exception as e:
        print(f"❌ Error clearing __pycache__ directories: {e}")
    
    # Clear .pyc files
    try:
        for pyc_file in project_root.rglob("*.pyc"):
            pyc_file.unlink()
            print(f"🗑️  Deleted .pyc file: {pyc_file.relative_to(project_root)}")
            deleted_count += 1
    except Exception as e:
        print(f"❌ Error clearing .pyc files: {e}")
    
    return deleted_count


def main():
    """
    Main function.
    """
    print("🧹 WIZARD-2.1 - Clear Cache Script")
    print("=" * 40)
    
    deleted_count = clear_cache()
    
    if deleted_count > 0:
        print(f"\n✅ Successfully deleted {deleted_count} cache item(s)")
        print("🎉 Cache clearing completed successfully!")
    else:
        print("\n✅ No cache files found to delete")
        print("🎉 Cache is already clean!")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
