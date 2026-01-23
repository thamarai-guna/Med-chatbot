"""
System Loader for Shared Medical Resources
Automatically processes medical books and creates shared vector store
Run once on first startup or when vector store is missing
"""

import os
import sys
from typing import List
import falcon
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


def load_shared_medical_books(force_rebuild: bool = False) -> bool:
    """
    Load shared medical books from resources/medical_books/
    Embed into vector_store/shared/
    
    Args:
        force_rebuild: If True, rebuild even if vector store exists
    
    Returns:
        True if successful, False otherwise
    """
    
    # Check if shared vector store already exists
    shared_vs_path = "vector store/shared"
    if os.path.exists(shared_vs_path) and not force_rebuild:
        print(f"✅ Shared medical books vector store already exists at {shared_vs_path}")
        return True
    
    print("🔄 Loading shared medical books...")
    
    # Check if resources directory exists
    resources_dir = "resources/medical_books"
    if not os.path.exists(resources_dir):
        print(f"⚠️ Medical books directory not found: {resources_dir}")
        print(f"ℹ️ Creating directory. Please add medical books (PDF/TXT) to this folder.")
        os.makedirs(resources_dir, exist_ok=True)
        return False
    
    # Find PDF and TXT files
    medical_files = []
    for filename in os.listdir(resources_dir):
        if filename.endswith(('.pdf', '.txt')):
            medical_files.append(os.path.join(resources_dir, filename))
    
    if not medical_files:
        print(f"⚠️ No medical books found in {resources_dir}")
        print(f"ℹ️ Please add PDF or TXT medical reference books to this folder.")
        return False
    
    print(f"📚 Found {len(medical_files)} medical book(s):")
    for file in medical_files:
        print(f"   - {os.path.basename(file)}")
    
    # Process each book
    combined_content = ""
    
    for file_path in medical_files:
        print(f"📖 Reading: {os.path.basename(file_path)}...")
        
        try:
            if file_path.endswith('.pdf'):
                with open(file_path, 'rb') as f:
                    content = falcon.read_pdf(f)
                    combined_content += content
                    print(f"   ✅ Extracted {len(content)} characters")
            elif file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = falcon.read_txt(f)
                    combined_content += content
                    print(f"   ✅ Extracted {len(content)} characters")
        except Exception as e:
            print(f"   ❌ Error reading {os.path.basename(file_path)}: {e}")
            continue
    
    if not combined_content:
        print("❌ No content extracted from medical books")
        return False
    
    print(f"📊 Total content: {len(combined_content)} characters")
    
    # Chunk the content
    print("🔄 Chunking documents...")
    chunk_size = 512
    chunk_overlap = 50
    
    try:
        split_docs = falcon.split_doc(combined_content, chunk_size, chunk_overlap)
        print(f"✅ Created {len(split_docs)} chunks")
    except Exception as e:
        print(f"❌ Error chunking documents: {e}")
        return False
    
    # Embed into shared vector store
    print("🔄 Creating embeddings and storing in vector database...")
    print("⏳ This may take several minutes depending on document size...")
    
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}
        )
        db = FAISS.from_documents(split_docs, embeddings)
        os.makedirs(os.path.dirname(shared_vs_path), exist_ok=True)
        db.save_local(shared_vs_path)
        print(f"✅ Shared medical books vector store created at {shared_vs_path}")
        print(f"📊 Total chunks embedded: {len(split_docs)}")
        return True
    
    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        return False


def verify_shared_vector_store() -> bool:
    """
    Verify that shared vector store exists and is accessible
    
    Returns:
        True if exists and valid, False otherwise
    """
    shared_vs_path = "vector store/shared"
    
    if not os.path.exists(shared_vs_path):
        return False
    
    # Check for FAISS index file
    index_file = os.path.join(shared_vs_path, "index.faiss")
    if not os.path.exists(index_file):
        print(f"⚠️ Vector store folder exists but index.faiss not found")
        return False
    
    print(f"✅ Shared medical books vector store verified at {shared_vs_path}")
    return True


def get_shared_books_info() -> dict:
    """
    Get information about shared medical books
    
    Returns:
        dict with book count, vector store status, etc.
    """
    resources_dir = "resources/medical_books"
    shared_vs_path = "vector store/shared"
    
    books = []
    if os.path.exists(resources_dir):
        for filename in os.listdir(resources_dir):
            if filename.endswith(('.pdf', '.txt')):
                books.append(filename)
    
    return {
        "books_directory": resources_dir,
        "books_count": len(books),
        "books": books,
        "vector_store_path": shared_vs_path,
        "vector_store_exists": os.path.exists(shared_vs_path),
        "status": "ready" if os.path.exists(shared_vs_path) else "needs_setup"
    }


if __name__ == "__main__":
    """
    Run this script to initialize shared medical books vector store
    
    Usage:
        python system_loader.py           # Load if not exists
        python system_loader.py --rebuild  # Force rebuild
    """
    
    print("=" * 60)
    print("SHARED MEDICAL BOOKS LOADER")
    print("=" * 60)
    
    force_rebuild = "--rebuild" in sys.argv or "-r" in sys.argv
    
    if force_rebuild:
        print("🔄 Force rebuild enabled")
    
    success = load_shared_medical_books(force_rebuild=force_rebuild)
    
    if success:
        print("\n✅ System loader completed successfully")
        print("ℹ️ Shared medical knowledge is now available for all patients")
    else:
        print("\n⚠️ System loader did not complete")
        print("ℹ️ Please add medical reference books to resources/medical_books/")
        print("ℹ️ Supported formats: PDF, TXT")
    
    print("=" * 60)
