#!/usr/bin/env python3
"""
Quick Update Script
Run this after pulling changes to sync dependencies and data
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_venv():
    """Check if virtual environment is activated"""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment activated")
        return True
    else:
        print("⚠️  Virtual environment not activated")
        print("   Run: .venv\\Scripts\\activate (Windows) or source .venv/bin/activate (Mac/Linux)")
        return False

def main():
    print("=" * 60)
    print("Quick Update - Pull & Sync")
    print("=" * 60)
    
    # Check venv
    if not check_venv():
        print("\n❌ Please activate virtual environment first")
        sys.exit(1)
    
    # Check if requirements changed
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        # Simple check: if requirements.txt was modified recently, suggest reinstall
        print("\n📦 Checking Python dependencies...")
        
        try:
            # Try importing a key package to verify environment
            import fastapi
            import sentence_transformers
            print("✅ Core packages present")
            
            # Ask if user wants to update anyway
            response = input("\n   Update packages? (y/N): ").strip().lower()
            if response == 'y':
                run_command(
                    f"{sys.executable} -m pip install -r requirements.txt",
                    "Installing/updating Python packages"
                )
        except ImportError:
            print("⚠️  Some packages missing - installing...")
            run_command(
                f"{sys.executable} -m pip install -r requirements.txt",
                "Installing Python packages"
            )
    
    # Check vector store
    shared_vs = Path("vector store/shared")
    if shared_vs.exists() and list(shared_vs.glob("*")):
        print("\n✅ Shared vector store present (pulled from repo)")
    else:
        print("\n⚠️  Shared vector store missing")
        response = input("   Build from Document-pdfs/? (y/N): ").strip().lower()
        if response == 'y':
            run_command(
                f"{sys.executable} system_loader.py",
                "Building shared vector store"
            )
    
    # Check frontend
    frontend_path = Path("frontend")
    if frontend_path.exists():
        node_modules = frontend_path / "node_modules"
        if not node_modules.exists():
            print("\n📦 Frontend dependencies missing")
            response = input("   Install frontend packages? (y/N): ").strip().lower()
            if response == 'y':
                run_command(
                    "cd frontend && npm install",
                    "Installing frontend dependencies"
                )
        else:
            print("\n✅ Frontend dependencies present")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ Update complete!")
    print("\nNext steps:")
    print("1. Backend: uvicorn backend_api:app --reload")
    print("2. Frontend: cd frontend && npm run dev")
    print("=" * 60)

if __name__ == "__main__":
    main()
