import streamlit as st
import os
import falcon
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
            Please Insert the Token and Select Vector Store, Temperature, and Maximum Character Length to create the chatbot.

            **NOTE:**
            - **Token:** API Key From Hugging Face.
            - **Temperature:** How much creative the chatbot will be? Don't Insert 0 or More Than 1.""")
        with st.form("setting"):
            row_1 = st.columns(3)
            with row_1[0]:
                text = st.text_input("Hugging Face Token (No need to insert)", type='password',value= f"{'*' * len(os.getenv('API_KEY'))}")

            with row_1[1]:
                llm_model = st.text_input("LLM model", value="meta-llama/Meta-Llama-3-8B")

            with row_1[2]:
                instruct_embeddings = st.text_input("Instruct Embeddings", value="sentence-transformers/all-MiniLM-L6-v2")

            row_2 = st.columns(3)
            with row_2[0]:
                vector_store_list = os.listdir("vector store/")
                default_choice = (
                    vector_store_list.index('naruto_snake')
                    if 'naruto_snake' in vector_store_list
                    else 0
                )
                existing_vector_store = st.selectbox("Vector Store", vector_store_list, default_choice)
            
            with row_2[1]:
                temperature = st.number_input("Temperature", value=1.0, step=0.1)

            with row_2[2]:
                max_length = st.number_input("Maximum character length", value=300, step=1)

            create_chatbot = st.form_submit_button("Launch chatbot")


    # Prepare the LLM model
    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    if token:
        st.session_state.conversation = falcon.prepare_rag_llm(
            token, existing_vector_store, temperature, max_length
        )

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

        # Answer the question
        answer, doc_source = falcon.generate_answer(question, token)
        with st.chat_message("assistant"):
            st.write(answer)
        # Append assistant answer to history
        st.session_state.history.append({"role": "assistant", "content": answer})

        # Append the document sources
        st.session_state.source.append({"question": question, "answer": answer, "document": doc_source})


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
