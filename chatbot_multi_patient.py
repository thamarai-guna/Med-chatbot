"""
Multi-Patient Medical Chatbot with Streamlit
Support for multiple patients with separate histories and risk tracking

⚠️ PROTOTYPE STATUS
This Streamlit UI is a prototype and reference implementation.
The production interface is the FastAPI backend (backend_api.py).

Both interfaces share the same SQLite database and AI logic:
- Chat responses are identical between Streamlit and FastAPI
- Patient data is unified across both interfaces
- This allows gradual migration from Streamlit to React+FastAPI

For production use: See API_DOCUMENTATION.md for FastAPI endpoint reference
For testing: Run: uvicorn backend_api:app --reload
"""

import streamlit as st
import sys
from rag_engine import RAGEngine
from patient_manager import get_patient_manager
import falcon

# Page configuration
st.set_page_config(
    page_title="Multi-Patient Medical Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "patient_id" not in st.session_state:
    st.session_state.patient_id = None
if "current_rag_engine" not in st.session_state:
    st.session_state.current_rag_engine = None
if "messages" not in st.session_state:
    st.session_state.messages = []


def sidebar_patient_management():
    """Patient management in sidebar"""
    st.sidebar.title("🏥 Patient Management")
    
    # Patient mode selection
    mode = st.sidebar.radio("Select Mode", ["Access Existing Patient", "Register New Patient"])
    
    if mode == "Register New Patient":
        st.sidebar.subheader("Register New Patient")
        patient_id = st.sidebar.text_input("Patient ID", placeholder="P001, patient_123, etc.")
        patient_name = st.sidebar.text_input("Patient Name", placeholder="John Doe")
        patient_email = st.sidebar.text_input("Email (optional)", placeholder="patient@hospital.com")
        patient_age = st.sidebar.number_input("Age (optional)", min_value=0, max_value=150, value=0)
        patient_history = st.sidebar.text_area("Medical History (optional)", placeholder="Any relevant medical conditions...")
        
        if st.sidebar.button("✅ Register Patient"):
            if patient_id and patient_name:
                pm = get_patient_manager()
                result = pm.register_patient(
                    patient_id=patient_id,
                    name=patient_name,
                    email=patient_email if patient_email else None,
                    age=patient_age if patient_age > 0 else None,
                    medical_history=patient_history
                )
                if result["success"]:
                    st.sidebar.success(f"✅ {result['message']}")
                    st.session_state.patient_id = patient_id
                else:
                    st.sidebar.error(f"❌ {result['message']}")
    
    else:  # Access Existing Patient
        st.sidebar.subheader("Access Patient Record")
        pm = get_patient_manager()
        patients = pm.get_all_patients()
        
        if patients:
            patient_options = {f"{p['name']} (ID: {p['patient_id']})": p['patient_id'] for p in patients}
            selected_patient = st.sidebar.selectbox(
                "Select Patient",
                options=patient_options.keys(),
                help="Choose a patient to access their records"
            )
            
            if selected_patient:
                selected_patient_id = patient_options[selected_patient]
                
                if st.sidebar.button("🔓 Access Patient"):
                    st.session_state.patient_id = selected_patient_id
                    st.session_state.messages = []
                    st.session_state.current_rag_engine = None
                    st.rerun()
        else:
            st.sidebar.info("No patients registered yet. Register a new patient first.")


def display_patient_info():
    """Display current patient information"""
    if st.session_state.patient_id:
        pm = get_patient_manager()
        patient = pm.get_patient(st.session_state.patient_id)
        
        if patient:
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"👤 **Patient**: {patient['name']}\n\n🆔 **ID**: {patient['patient_id']}")
            with col2:
                risk_summary = pm.get_patient_risk_summary(st.session_state.patient_id)
                st.info(
                    f"📊 **Risk Summary (Last 30 days)**\n\n"
                    f"Total Queries: {risk_summary['total_queries']}\n\n"
                    f"Max Risk Level: **{risk_summary['max_risk_level']}**\n\n"
                    f"CRITICAL: {risk_summary['risk_distribution']['CRITICAL']} | "
                    f"HIGH: {risk_summary['risk_distribution']['HIGH']} | "
                    f"MEDIUM: {risk_summary['risk_distribution']['MEDIUM']}"
                )


def initialize_rag_engine(vector_store_name: str):
    """Initialize RAG engine for current patient"""
    if not st.session_state.patient_id:
        st.error("❌ No patient selected. Please select or register a patient first.")
        return None
    
    try:
        engine = RAGEngine(
            vector_store_name=vector_store_name,
            patient_id=st.session_state.patient_id,
            max_tokens=500,
            temperature=0.7
        )
        st.session_state.current_rag_engine = engine
        return engine
    except Exception as e:
        st.error(f"❌ Error initializing RAG engine: {str(e)}")
        return None


def chat_interface():
    """Chat interface for medical Q&A"""
    st.subheader("💬 Medical Chat")
    
    # Get available vector stores
    import os
    vs_dir = "vector store"
    if os.path.exists(vs_dir):
        vector_stores = [d for d in os.listdir(vs_dir) if os.path.isdir(os.path.join(vs_dir, d))]
    else:
        vector_stores = []
    
    if not vector_stores:
        st.warning("⚠️ No vector stores available. Please upload documents first.")
        return
    
    selected_vs = st.selectbox("Select Knowledge Base", vector_stores)
    
    # Initialize RAG engine
    if st.session_state.current_rag_engine is None:
        st.session_state.current_rag_engine = initialize_rag_engine(selected_vs)
    
    if st.session_state.current_rag_engine is None:
        return
    
    # Display chat history
    st.write("---")
    for msg in st.session_state.messages:
        with st.chat_message("user"):
            st.write(msg["question"])
        with st.chat_message("assistant"):
            st.write(msg["answer"])
            
            # Risk level display with color coding
            risk_colors = {
                "CRITICAL": "🔴",
                "HIGH": "🟠",
                "MEDIUM": "🟡",
                "LOW": "🟢",
                "UNKNOWN": "⚪"
            }
            risk_color = risk_colors.get(msg["risk_level"], "⚪")
            st.markdown(f"{risk_color} **Risk Level**: {msg['risk_level']} - {msg['risk_reason']}")
            
            if msg["source_documents"]:
                with st.expander("📚 Source Documents"):
                    for doc in msg["source_documents"][:3]:
                        st.text(doc[:200] + "..." if len(doc) > 200 else doc)
    
    # Chat input
    user_input = st.chat_input("Ask a medical question...", key="chat_input")
    
    if user_input:
        # Add user message
        st.session_state.messages.append({
            "question": user_input,
            "answer": "",
            "risk_level": "",
            "risk_reason": ""
        })
        
        # Get answer
        with st.spinner("🔄 Analyzing your question..."):
            response = st.session_state.current_rag_engine.answer_question(user_input)
        
        # Update last message with response
        st.session_state.messages[-1].update({
            "answer": response["answer"],
            "risk_level": response["risk_level"],
            "risk_reason": response["risk_reason"],
            "source_documents": response["source_documents"]
        })
        
        st.rerun()


def document_upload_interface():
    """Document upload and vector store creation"""
    st.subheader("📄 Document Management")
    
    with st.form("upload_form"):
        # Chunking parameters
        col1, col2 = st.columns(2)
        with col1:
            chunk_size = st.number_input("Chunk Size", value=512, step=64)
        with col2:
            chunk_overlap = st.number_input("Chunk Overlap", value=50, step=10)
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload PDF or TXT files",
            type=["pdf", "txt"],
            accept_multiple_files=True
        )
        
        # Vector store settings
        col1, col2 = st.columns(2)
        with col1:
            existing_vector_stores = []
            if os.path.exists("vector store"):
                existing_vector_stores = [d for d in os.listdir("vector store") 
                                         if os.path.isdir(os.path.join("vector store", d))]
            
            vector_store_option = st.selectbox(
                "Vector Store Option",
                ["<Create New>"] + existing_vector_stores
            )
        
        with col2:
            new_vs_name = st.text_input(
                "Vector Store Name",
                value="new_knowledge_base"
            )
        
        submit = st.form_submit_button("📤 Upload & Save")
    
    if submit and uploaded_files:
        # Process documents
        st.info(f"📊 Processing {len(uploaded_files)} file(s)...")
        
        combined_content = ""
        for file in uploaded_files:
            if file.name.endswith(".pdf"):
                combined_content += falcon.read_pdf(file)
            elif file.name.endswith(".txt"):
                combined_content += falcon.read_txt(file)
        
        # Show progress for chunking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.write("🔄 Chunking document...")
        progress_bar.progress(25)
        
        split = falcon.split_doc(combined_content, chunk_size, chunk_overlap)
        progress_bar.progress(50)
        
        status_text.write(f"✅ Chunking complete: {len(split)} chunks created")
        progress_bar.progress(100)
        
        # Save to vector store
        create_new = vector_store_option == "<Create New>"
        falcon.embedding_storing(
            split,
            create_new,
            "" if create_new else vector_store_option,
            new_vs_name
        )
        
        st.success("✅ Documents saved successfully!")


def patient_history_view():
    """View detailed patient history"""
    st.subheader("📋 Patient History")
    
    if not st.session_state.patient_id:
        st.warning("Please select a patient first")
        return
    
    pm = get_patient_manager()
    history = pm.get_patient_history(st.session_state.patient_id, limit=100)
    
    if history:
        for i, record in enumerate(history, 1):
            with st.expander(f"Query {i}: {record['question'][:50]}..."):
                st.write(f"**Question**: {record['question']}")
                st.write(f"**Answer**: {record['answer']}")
                risk_colors = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠",
                    "MEDIUM": "🟡",
                    "LOW": "🟢",
                    "UNKNOWN": "⚪"
                }
                st.markdown(f"{risk_colors.get(record['risk_level'], '⚪')} **Risk Level**: {record['risk_level']}")
                st.write(f"**Risk Reason**: {record['risk_reason']}")
                st.caption(f"Timestamp: {record['timestamp']}")
    else:
        st.info("No chat history for this patient yet.")


def main():
    """Main application"""
    st.title("🏥 Multi-Patient Medical Chatbot")
    
    # Sidebar patient management
    sidebar_patient_management()
    
    if not st.session_state.patient_id:
        st.info("👈 Please register or select a patient from the sidebar to get started.")
        return
    
    # Display patient info
    display_patient_info()
    st.write("---")
    
    # Tabs for different features
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📄 Documents", "📋 History"])
    
    with tab1:
        chat_interface()
    
    with tab2:
        document_upload_interface()
    
    with tab3:
        patient_history_view()


if __name__ == "__main__":
    main()
