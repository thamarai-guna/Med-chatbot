# Medical Report Upload Engine
# Handles PDF/Image/Text extraction, chunking, embedding, and vector storage
# Creates patient-specific vector stores for RAG integration

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


class ReportProcessor:
    """Process medical reports: extract text, chunk, embed, and store in vector DB"""
    
    def __init__(self):
        """Initialize embeddings model"""
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        # Text splitter for chunking
        self.splitter = CharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separator="\n"
        )
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            from pypdf import PdfReader
            
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PdfReader(f)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return text
        except ImportError:
            raise RuntimeError("pypdf not installed. Install with: pip install pypdf")
        except Exception as e:
            raise RuntimeError(f"Failed to extract PDF text: {str(e)}")
    
    def extract_text_from_image(self, file_path: str) -> str:
        """
        Extract text from image using OCR
        
        Args:
            file_path: Path to image file (jpg, png, etc.)
            
        Returns:
            Extracted text via OCR
        """
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            
            return text
        except ImportError:
            raise RuntimeError(
                "pytesseract not installed. Install with: pip install pytesseract\n"
                "Also requires Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from image: {str(e)}")
    
    def extract_text_from_plain_text(self, file_path: str) -> str:
        """
        Read plain text file
        
        Args:
            file_path: Path to text file
            
        Returns:
            File contents
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read text file: {str(e)}")
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text: remove extra whitespace, normalize formatting
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)
        
        # Remove multiple consecutive newlines
        while '\n\n\n' in text:
            text = text.replace('\n\n\n', '\n\n')
        
        return text
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into meaningful chunks for embedding
        
        Args:
            text: Cleaned text to chunk
            
        Returns:
            List of text chunks
        """
        chunks = self.splitter.split_text(text)
        return [chunk for chunk in chunks if len(chunk.strip()) > 50]
    
    def process_report(self, file_path: str) -> Tuple[bool, str, List[str]]:
        """
        Complete processing pipeline: extract -> clean -> chunk
        
        Args:
            file_path: Path to medical report file
            
        Returns:
            (success: bool, message: str, chunks: List[str])
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            # Extract text based on file type
            if file_ext == '.pdf':
                raw_text = self.extract_text_from_pdf(file_path)
                source_type = "PDF"
            elif file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                raw_text = self.extract_text_from_image(file_path)
                source_type = "Image (OCR)"
            elif file_ext in ['.txt']:
                raw_text = self.extract_text_from_plain_text(file_path)
                source_type = "Plain Text"
            else:
                return False, f"Unsupported file type: {file_ext}", []
            
            # Clean text
            clean_text = self.clean_text(raw_text)
            
            if len(clean_text.strip()) < 50:
                return False, "Extracted text is too short. Please check the file.", []
            
            # Chunk text
            chunks = self.chunk_text(clean_text)
            
            if not chunks:
                return False, "Could not split text into meaningful chunks.", []
            
            message = f"Successfully processed {source_type} report: {len(chunks)} chunks extracted"
            return True, message, chunks
        
        except Exception as e:
            return False, f"Error processing report: {str(e)}", []


class PatientVectorStoreManager:
    """Manage patient-specific vector stores and embeddings"""
    
    def __init__(self):
        """Initialize embeddings model"""
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.base_path = "vector store"
        os.makedirs(self.base_path, exist_ok=True)
    
    def get_patient_store_path(self, patient_id: str) -> str:
        """Get path for patient-specific vector store"""
        return os.path.join(self.base_path, f"patient_{patient_id}")
    
    def patient_has_reports(self, patient_id: str) -> bool:
        """Check if patient has indexed reports"""
        path = self.get_patient_store_path(patient_id)
        return os.path.exists(path) and os.path.isdir(path)
    
    def create_or_update_vector_store(
        self, 
        patient_id: str, 
        text_chunks: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """
        Create or update patient's vector store with embeddings
        
        Args:
            patient_id: Patient identifier
            text_chunks: List of text chunks to embed
            metadata: Optional metadata for chunks
            
        Returns:
            (success: bool, message: str)
        """
        try:
            store_path = self.get_patient_store_path(patient_id)
            
            # Create metadata for each chunk
            metadatas = []
            for i, chunk in enumerate(text_chunks):
                meta = {
                    "patient_id": patient_id,
                    "chunk_index": i,
                    "timestamp": datetime.utcnow().isoformat()
                }
                if metadata:
                    meta.update(metadata)
                metadatas.append(meta)
            
            # Create FAISS vector store
            if self.patient_has_reports(patient_id):
                # Update existing store
                vector_db = FAISS.load_local(
                    store_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                vector_db.add_texts(text_chunks, metadatas=metadatas)
                vector_db.save_local(store_path)
                message = f"Updated patient vector store with {len(text_chunks)} new chunks"
            else:
                # Create new store
                vector_db = FAISS.from_texts(
                    text_chunks,
                    self.embeddings,
                    metadatas=metadatas
                )
                vector_db.save_local(store_path)
                message = f"Created patient vector store with {len(text_chunks)} chunks"
            
            return True, message
        
        except Exception as e:
            return False, f"Failed to create/update vector store: {str(e)}"
    
    def delete_patient_vector_store(self, patient_id: str) -> Tuple[bool, str]:
        """
        Delete patient's vector store (e.g., for privacy/data deletion)
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            (success: bool, message: str)
        """
        try:
            store_path = self.get_patient_store_path(patient_id)
            if os.path.exists(store_path):
                shutil.rmtree(store_path)
                return True, f"Deleted vector store for patient {patient_id}"
            else:
                return False, f"No vector store found for patient {patient_id}"
        except Exception as e:
            return False, f"Failed to delete vector store: {str(e)}"


class ReportUploadHandler:
    """
    Main orchestrator for report upload flow:
    1. Receive file
    2. Extract text
    3. Clean and chunk
    4. Generate embeddings
    5. Store in patient vector DB
    6. Mark patient as having reports (gating flag)
    """
    
    def __init__(self):
        """Initialize components"""
        self.processor = ReportProcessor()
        self.vector_manager = PatientVectorStoreManager()
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def save_uploaded_file(self, file_content: bytes, original_filename: str) -> Tuple[bool, str]:
        """
        Save uploaded file to temporary directory
        
        Args:
            file_content: File bytes
            original_filename: Original filename from upload
            
        Returns:
            (success: bool, file_path: str)
        """
        try:
            # Use original filename to preserve extension
            file_path = os.path.join(self.upload_dir, original_filename)
            
            # Ensure unique filename
            if os.path.exists(file_path):
                base, ext = os.path.splitext(original_filename)
                counter = 1
                while os.path.exists(os.path.join(self.upload_dir, f"{base}_{counter}{ext}")):
                    counter += 1
                file_path = os.path.join(self.upload_dir, f"{base}_{counter}{ext}")
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            return True, file_path
        except Exception as e:
            return False, f"Failed to save file: {str(e)}"
    
    def process_and_index_report(
        self,
        patient_id: str,
        file_path: str,
        filename: str
    ) -> Dict[str, Any]:
        """
        Complete pipeline: extract text -> chunk -> embed -> store
        
        Args:
            patient_id: Patient identifier
            file_path: Path to uploaded file
            filename: Original filename
            
        Returns:
            Status dictionary with success/messages
        """
        result = {
            "success": False,
            "patient_id": patient_id,
            "filename": filename,
            "message": "",
            "chunks_count": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Step 1: Extract text
            success, extract_msg, chunks = self.processor.process_report(file_path)
            
            if not success:
                result["message"] = f"Text extraction failed: {extract_msg}"
                return result
            
            result["chunks_count"] = len(chunks)
            
            # Step 2: Create/update vector store
            metadata = {
                "source_file": filename,
                "source_type": Path(file_path).suffix.lower()
            }
            
            success, store_msg = self.vector_manager.create_or_update_vector_store(
                patient_id,
                chunks,
                metadata
            )
            
            if not success:
                result["message"] = f"Vector store creation failed: {store_msg}"
                return result
            
            # Step 3: Mark as successful
            result["success"] = True
            result["message"] = f"{extract_msg}\n{store_msg}"
            
            return result
        
        except Exception as e:
            result["message"] = f"Unexpected error: {str(e)}"
            return result
        
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
    
    def get_upload_status(self, patient_id: str) -> Dict[str, Any]:
        """
        Get patient's report upload status
        
        Returns:
            Status dict with has_medical_report flag
        """
        has_reports = self.vector_manager.patient_has_reports(patient_id)
        
        return {
            "patient_id": patient_id,
            "has_medical_report": has_reports,
            "status": "Ready for monitoring" if has_reports else "Awaiting medical report upload",
            "can_proceed_with_monitoring": has_reports
        }


# Singleton instance
_handler_instance = None

def get_upload_handler() -> ReportUploadHandler:
    """Get or create singleton instance"""
    global _handler_instance
    if _handler_instance is None:
        _handler_instance = ReportUploadHandler()
    return _handler_instance
