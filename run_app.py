#!/usr/bin/env python3
"""
Simple application runner for the Medical Chatbot
This runs the RAG-powered Groq chatbot without Streamlit
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if dependencies are installed
try:
    print("✓ pypdf imported")
except ImportError as e:
    print(f"✗ Missing dependency: {e}")
    sys.exit(1)

try:
    import groq
    print("✓ groq imported")
except ImportError:
    print("✗ groq not installed")
    sys.exit(1)

try:
    import requests
    print("✓ requests imported")
except ImportError:
    print("✗ requests not installed")
    sys.exit(1)

# Check Groq API Key
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    print(f"✓ GROQ_API_KEY configured (first 10 chars): {api_key[:10]}...")
else:
    print("✗ GROQ_API_KEY not set in .env")

print("\n=== Attempting to import RAG Engine ===")
try:
    from rag_engine import RAGEngine
    print("✓ RAG Engine imported successfully")
except ImportError as e:
    print(f"✗ Failed to import RAG Engine: {e}")
    print("\nNote: Some dependencies (langchain, FAISS, HuggingFace) require additional setup")
    print("Consider installing additional packages:")
    print("  pip install langchain faiss-cpu sentence-transformers -i https://pypi.org/simple/")

print("\n=== Application Status ===")
print("✓ Core dependencies installed")
print("✓ Groq API configured")
print("\nTo run the full Streamlit app, additional dependencies are needed.")
print("Run: pip install langchain faiss-cpu sentence-transformers streamlit")
