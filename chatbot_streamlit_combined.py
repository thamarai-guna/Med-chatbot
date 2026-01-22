import streamlit as st
import os
import falcon
import rag_engine
from rag_engine import RAGEngine
import torch
import time
import gc
from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo
from dotenv import load_dotenv
load_dotenv()

token=os.getenv("API_KEY")
# Memory management functions
def clear_gpu_memory():
    torch.cuda.empty_cache()
    gc.collect()

def wait_until_enough_gpu_memory(min_memory_available, max_retries=10, sleep_time=5):
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(torch.cuda.current_device())

    for _ in range(max_retries):
        info = nvmlDeviceGetMemoryInfo(handle)
        if info.free >= min_memory_available:
            break
        print(f"Waiting for {min_memory_available} bytes of free GPU memory. Retrying in {sleep_time} seconds...")
        time.sleep(sleep_time)
    else:
        raise RuntimeError(f"Failed to acquire {min_memory_available} bytes of free GPU memory after {max_retries} retries.")

def main():
    # Call memory management functions before starting Streamlit app
    #min_memory_available = 1 * 1024 * 1024 * 1024  # 1GB
    clear_gpu_memory()
    #wait_until_enough_gpu_memory(min_memory_available)

    st.sidebar.title("Select From The List Below: ")
    selection = st.sidebar.radio("GO TO: ", ["Document Embedding","RAG Chatbot", ])

    if selection == "Document Embedding":
        display_document_embedding_page()

    elif selection == "RAG Chatbot":
        display_chatbot_page()
   

def display_chatbot_page():

    st.title("Multi Source Chatbot")

    # Setting the LLM
    with st.expander("Initialize the LLM Model"):
        
        st.markdown("""
            Please Select Vector Store, Temperature, and Maximum Token Length to create the chatbot.

            **NOTE:**
            - **Groq API:** Set GROQ_API_KEY in your .env file
            - **Temperature:** Creativity level (0.0 = focused, 1.0 = creative)
            - **Max Tokens:** Maximum response length (keep low to reduce costs)
            """)
        with st.form("setting"):
            row_1 = st.columns(2)
            with row_1[0]:
                vector_store_list = os.listdir("vector store/")
                default_choice = (
                    vector_store_list.index('naruto_snake')
                    if 'naruto_snake' in vector_store_list
                    else 0
                )
                existing_vector_store = st.selectbox("Vector Store", vector_store_list, default_choice)
            
            with row_1[1]:
                temperature = st.number_input("Temperature", value=0.7, step=0.1, min_value=0.0, max_value=1.0)

            max_length = st.number_input("Maximum tokens", value=500, step=50, min_value=100, max_value=2000)

            create_chatbot = st.form_submit_button("Launch chatbot")


    # Prepare the RAG Engine
    if "rag_engine" not in st.session_state:
        st.session_state.rag_engine = None

    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key and create_chatbot:
        try:
            st.session_state.rag_engine = RAGEngine(
                vector_store_name=existing_vector_store,
                max_tokens=max_length,
                temperature=temperature
            )
            st.success("✅ Chatbot initialized successfully!")
        except Exception as e:
            st.error(f"Error initializing chatbot: {str(e)}")

    # Chat history
    if "history" not in st.session_state:
        st.session_state.history = []

    # Source documents
    if "source" not in st.session_state:
        st.session_state.source = []

    # Display chats
    for message in st.session_state.history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Ask a question
    if question := st.chat_input("Ask a question"):
        # Append user question to history
        st.session_state.history.append({"role": "user", "content": question})
        # Add user question
        with st.chat_message("user"):
            st.markdown(question)

        # Answer the question using RAG Engine
        if st.session_state.rag_engine is None:
            with st.chat_message("assistant"):
                st.error("Please initialize the chatbot first by clicking 'Launch chatbot'")
        else:
            result = st.session_state.rag_engine.answer_question(question)
            
            answer = result["answer"]
            risk_level = result["risk_level"]
            risk_reason = result["risk_reason"]
            doc_source = result["source_documents"]
            
            with st.chat_message("assistant"):
                st.write(answer)
                
                # Display risk assessment with color coding
                if risk_level == "CRITICAL":
                    st.error(f"🚨🚨 CRITICAL RISK: {risk_reason}")
                    st.error("⚠️ SEEK IMMEDIATE EMERGENCY MEDICAL CARE - CALL 911")
                elif risk_level == "HIGH":
                    st.error(f"🚨 HIGH RISK: {risk_reason}")
                    st.warning("Urgent medical attention recommended within hours")
                elif risk_level == "MEDIUM":
                    st.warning(f"⚠️ MEDIUM RISK: {risk_reason}")
                    st.info("Medical evaluation recommended soon")
                elif risk_level == "LOW":
                    st.info(f"ℹ️ LOW RISK: {risk_reason}")
                else:
                    st.info(f"ℹ️ Risk Level: {risk_level} - {risk_reason}")
            
            # Append assistant answer to history
            st.session_state.history.append({"role": "assistant", "content": answer})

            # Append the document sources with risk info
            st.session_state.source.append({
                "question": question, 
                "answer": answer, 
                "risk_level": risk_level,
                "risk_reason": risk_reason,
                "document": doc_source
            })


    # Source documents
    with st.expander("Chat History and Source Information"):
        st.write(st.session_state.source)

def display_document_embedding_page():
    st.title("Document Embedding Page")
    st.markdown("""This page is used to upload the documents as the custom knowledge base for the chatbot.
                  **NOTE:** If you are uploading a new file (for the first time) please insert a new vector store name to store it in vector database
                """)

    with st.form("document_input"):
        
        document = st.file_uploader(
            "Knowledge Documents", type=['pdf', 'txt'], help=".pdf or .txt file", accept_multiple_files= True
        )

        row_1 = st.columns([2, 1, 1])
        with row_1[0]:
            instruct_embeddings = st.text_input(
                "Model Name of the Instruct Embeddings", value="sentence-transformers/all-MiniLM-L6-v2"
            )
        
        with row_1[1]:
            chunk_size = st.number_input(
                "Chunk Size", value=200, min_value=0, step=1,
            )
        
        with row_1[2]:
            chunk_overlap = st.number_input(
                "Chunk Overlap", value=10, min_value=0, step=1,
                help="Lower than chunk size"
            )
        
        row_2 = st.columns(2)
        with row_2[0]:
            # List the existing vector stores
            vector_store_list = os.listdir("vector store/")
            vector_store_list = ["<New>"] + vector_store_list
            
            existing_vector_store = st.selectbox(
                "Vector Store to Merge the Knowledge", vector_store_list,
                help="""
                Which vector store to add the new documents.
                Choose <New> to create a new vector store.
                    """
            )

        with row_2[1]:
            # List the existing vector stores     
            new_vs_name = st.text_input(
                "New Vector Store Name", value="new_vector_store_name",
                help="""
                If choose <New> in the dropdown / multiselect box,
                name the new vector store. Otherwise, fill in the existing vector
                store to merge.
                """
            )

        save_button = st.form_submit_button("Save vector store")

    if save_button:
        if document is not None:
            # Aggregate content of all uploaded files
            combined_content = ""
            for file in document:
                if file.name.endswith(".pdf"):
                    combined_content += falcon.read_pdf(file)
                elif file.name.endswith(".txt"):
                    combined_content += falcon.read_txt(file)
                else:
                    st.error("Check if the uploaded file is .pdf or .txt")

            # Split combined content into chunks
            split = falcon.split_doc(combined_content, chunk_size, chunk_overlap)

            # Check whether to create new vector store
            create_new_vs = None
            if existing_vector_store == "<New>" and new_vs_name != "":
                create_new_vs = True
            elif existing_vector_store != "<New>" and new_vs_name != "":
                create_new_vs = False
            else:
                st.error("Check the 'Vector Store to Merge the Knowledge' and 'New Vector Store Name'")

            # Embeddings and storing
            falcon.embedding_storing(split, create_new_vs, existing_vector_store, new_vs_name)
            print(f'"Document info":{combined_content}')    
            print(f'"Splitted info":{split}')   

        else:
            st.warning("Please upload at least one file.")



if __name__ == "__main__":
    main()
