#!/usr/bin/env python3
"""
Setup Verification Script
Checks if all dependencies are installed and configured correctly
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Need 3.10+")
        return False

def check_imports():
    """Check critical imports"""
    imports = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "langchain": "LangChain",
        "sentence_transformers": "Sentence Transformers",
        "faiss": "FAISS",
        "dotenv": "Python Dotenv"
    }
    
    all_ok = True
    for module, name in imports.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - Run: pip install -r requirements.txt")
            all_ok = False
    
    return all_ok

def check_env_file():
    """Check .env file exists"""
    if Path(".env").exists():
        with open(".env") as f:
            content = f.read()
            if "GROQ_API_KEY" in content and "your_" not in content:
                print("✅ .env file with GROQ_API_KEY")
                return True
            else:
                print("⚠️  .env exists but GROQ_API_KEY not set properly")
                return False
    else:
        print("❌ .env file not found - Copy .env.example and add your key")
        return False

def check_vector_store():
    """Check if shared vector store exists"""
    shared_path = Path("vector store/shared")
    if shared_path.exists() and list(shared_path.glob("*")):
        print("✅ Shared vector store exists")
        return True
    else:
        print("⚠️  Shared vector store missing - Run: python system_loader.py")
        return False

def check_frontend():
    """Check frontend setup"""
    frontend_path = Path("frontend")
    if frontend_path.exists():
        package_json = frontend_path / "package.json"
        node_modules = frontend_path / "node_modules"
        
        if package_json.exists():
            print("✅ Frontend package.json found")
            if node_modules.exists():
                print("✅ Frontend dependencies installed")
                return True
            else:
                print("⚠️  Frontend dependencies missing - Run: cd frontend && npm install")
                return False
        else:
            print("❌ Frontend package.json missing")
            return False
    else:
        print("❌ Frontend directory not found")
        return False

def main():
    print("=" * 50)
    print("Medical Chatbot Setup Verification")
    print("=" * 50)
    print()
    
    results = []
    
    print("Python Environment:")
    results.append(check_python_version())
    print()
    
    print("Python Dependencies:")
    results.append(check_imports())
    print()
    
    print("Configuration:")
    results.append(check_env_file())
    print()
    
    print("Vector Store:")
    check_vector_store()  # Warning only, not blocking
    print()
    
    print("Frontend:")
    check_frontend()  # Warning only, not blocking
    print()
    
    print("=" * 50)
    if all(results):
        print("✅ All critical checks passed!")
        print("\nNext steps:")
        print("1. Start backend: uvicorn backend_api:app --reload")
        print("2. Start frontend: cd frontend && npm run dev")
        print("3. Visit: http://localhost:5173")
    else:
        print("❌ Some checks failed - see above for fixes")
        sys.exit(1)

if __name__ == "__main__":
    main()
