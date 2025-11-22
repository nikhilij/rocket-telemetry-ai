#!/usr/bin/env python3
"""
Cleanup script to remove temporary and generated files.

Usage:
    python scripts/cleanup.py
"""

import os
import glob
import shutil


def cleanup():
    """Remove temporary and generated files from the project."""

    print("🧹 Cleaning up project directory...")
    print("=" * 60)

    # Files to remove
    patterns = [
        # Celery and Redis
        "celerybeat-schedule*",
        "dump.rdb",
        "*.rdb",
        # Python artifacts (only in project directories, not venv)
        "app/__pycache__",
        "tests/__pycache__",
        "scripts/**/__pycache__",
        "app/*.pyc",
        "tests/**/*.pyc",
        "scripts/**/*.pyc",
        "app/**/.pytest_cache",
        "tests/**/.pytest_cache",
        # Temporary files
        ".tmp_*",
        "*.tmp",
        "*.log",
        # IDE files
        ".DS_Store",
        "Thumbs.db",
        # Generated images (optional)
        # "*.png",  # Uncomment if you want to remove all PNG files
        "image.png",  # Specific unwanted image
    ]

    removed_count = 0

    for pattern in patterns:
        if "**" in pattern:
            # Recursive pattern
            for item in glob.glob(pattern, recursive=True):
                try:
                    if os.path.isfile(item):
                        os.remove(item)
                        print(f"✅ Removed file: {item}")
                        removed_count += 1
                    elif os.path.isdir(item):
                        shutil.rmtree(item)
                        print(f"✅ Removed directory: {item}")
                        removed_count += 1
                except Exception as e:
                    print(f"⚠️  Could not remove {item}: {e}")
        else:
            # Simple pattern
            for item in glob.glob(pattern):
                try:
                    if os.path.isfile(item):
                        os.remove(item)
                        print(f"✅ Removed: {item}")
                        removed_count += 1
                except Exception as e:
                    print(f"⚠️  Could not remove {item}: {e}")

    print("=" * 60)
    print(f"🎉 Cleanup complete! Removed {removed_count} items.")
    print("\nNote: Runtime files (celerybeat-schedule, dump.rdb) will be")
    print("regenerated when you start Celery and Redis services.")


if __name__ == "__main__":
    cleanup()
