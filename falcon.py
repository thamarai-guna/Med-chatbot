"""
Document Processing Utilities
Handles PDF/TXT reading, text splitting, and vector store management
"""

import streamlit as st
from pypdf import PdfReader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import time

load_dotenv()


def read_pdf(file):
    document = ""

    reader = PdfReader(file)
    for page in reader.pages:
        document += page.extract_text()

    return document


def read_txt(file):
    document = str(file.getvalue())
    document = document.replace("\\n", " \\n ").replace("\\r", " \\r ")

    return document


def split_doc(document, chunk_size, chunk_overlap):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    split = splitter.split_text(document)
    split = splitter.create_documents(split)

    return split


def embedding_storing(split, create_new_vs, existing_vector_store, new_vs_name):
    if create_new_vs is not None:
        # Show progress information
        st.info(f"📊 Processing {len(split)} document chunks...")
        
        # Estimate processing time based on number of chunks
        # Typically ~0.5-1 second per chunk for embeddings
        estimated_time = len(split) * 0.75  # seconds
        st.write(f"⏱️ Estimated time: ~{estimated_time:.0f} seconds ({estimated_time/60:.1f} minutes)")
        
        # Create progress bar and status placeholder
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        start_time = time.time()
        
        try:
            # Step 1: Load embeddings model
            status_text.write("🔄 Step 1/3: Loading embedding model...")
            progress_bar.progress(10)
            
            instructor_embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2", 
                model_kwargs={'device': 'cpu'}
            )
            
            # Step 2: Creating embeddings for documents
            status_text.write(f"🔄 Step 2/3: Creating embeddings for {len(split)} chunks...")
            progress_bar.progress(30)
            
            db = FAISS.from_documents(split, instructor_embeddings)
            
            elapsed_time = time.time() - start_time
            
            # Step 3: Saving vector store
            status_text.write("🔄 Step 3/3: Saving vector store...")
            progress_bar.progress(70)
            
            if create_new_vs == True:
                # Save db
                db.save_local("vector store/" + new_vs_name)
            else:
                # Load existing db
                load_db = FAISS.load_local(
                    "vector store/" + existing_vector_store,
                    instructor_embeddings,
                    allow_dangerous_deserialization=True
                )
                # Merge two DBs and save
                load_db.merge_from(db)
                load_db.save_local("vector store/" + new_vs_name)
            
            progress_bar.progress(100)
            
            total_time = time.time() - start_time
            status_text.write(f"✅ Step 3/3: Saved successfully!")
            
            st.success(f"✅ The document has been saved. Total time: {total_time:.1f} seconds")
            st.write(f"📈 Processed {len(split)} chunks in {total_time:.1f} seconds ({len(split)/total_time:.1f} chunks/sec)")
            
        except Exception as e:
            status_text.write(f"❌ Error occurred")
            progress_bar.progress(0)
            st.error(f"Error during embedding process: {str(e)}")

