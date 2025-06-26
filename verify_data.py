#!/usr/bin/env python3
"""Verify that all required data files are accessible in the container."""

import os
from pathlib import Path

def check_file(path, description):
    """Check if a file exists and is readable."""
    exists = os.path.exists(path)
    readable = os.access(path, os.R_OK) if exists else False
    size = os.path.getsize(path) if exists else 0
    
    status = "✅" if exists and readable else "❌"
    print(f"{status} {description}: {path}")
    if exists:
        print(f"   - Readable: {'Yes' if readable else 'No'}")
        print(f"   - Size: {size:,} bytes")
    else:
        print(f"   - File not found")
    return exists and readable

def main():
    print("=== Data Files Verification ===\n")
    
    # Check current working directory
    print(f"Current working directory: {os.getcwd()}")
    print(f"Data directory path: {Path('data').absolute()}\n")
    
    all_good = True
    
    # Check backgrounds
    print("📁 Backgrounds:")
    all_good &= check_file("data/backgrounds/background_1.jpg", "Background 1")
    all_good &= check_file("data/backgrounds/background_2.jpg", "Background 2")
    print()
    
    # Check audio
    print("📁 Audio:")
    all_good &= check_file("data/audio/background-music-1.mp3", "Background Music")
    print()
    
    # Check fonts
    print("📁 Fonts:")
    all_good &= check_file("data/fonts/RobotoSerif-Regular.ttf", "Roboto Serif Font")
    print()
    
    # Check database
    print("📁 Database:")
    all_good &= check_file("data/quotes/quotes.db", "Quotes Database")
    print()
    
    # List all files in data directory
    print("📂 Full data directory structure:")
    for root, dirs, files in os.walk("data"):
        level = root.replace("data", "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")
    
    print("\n" + "="*40)
    if all_good:
        print("✅ All required files are present and readable!")
    else:
        print("❌ Some files are missing or not readable!")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    exit(main())