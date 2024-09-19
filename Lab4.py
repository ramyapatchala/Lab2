import chromadb
from PyPDF2 import PdfReader
import streamlit as st
from openai.embeddings_utils import get_embedding
import openai

# Set your OpenAI API Key (you'll need to configure it elsewhere in your app)
openai.api_key = "YOUR_OPENAI_API_KEY"

# Function to read PDFs and extract text
def read_pdfs_to_text(uploaded_files):
    pdf_texts = {}
    for uploaded_file in uploaded_files:
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
        pdf_texts[uploaded_file.name] = text
    return pdf_texts

# Function to create and store vector database in session state
def create_lab4_vector_db():
    # Only create the collection if it doesn't already exist
    if 'Lab4_vectorDB' not in st.session_state:
        # Initialize ChromaDB Client
        chroma_client = chromadb.Client()
        
        # Create ChromaDB collection
        collection = chroma_client.create_collection(name="Lab4Collection")
        
        # Upload PDF files
        uploaded_files = st.file_uploader("Upload 7 PDF files", type="pdf", accept_multiple_files=True)
        
        # Ensure 7 PDFs are uploaded
        if uploaded_files and len(uploaded_files) == 7:
            pdf_texts = read_pdfs_to_text(uploaded_files)
            
            for filename, text in pdf_texts.items():
                # Generate embeddings using OpenAI
                embedding = get_embedding(text, engine="text-embedding-ada-002")  # Example embedding model
                
                # Add document with embedding to ChromaDB collection
                collection.add(
                    embeddings=[embedding],
                    documents=[text],
                    metadatas=[{"filename": filename}]
                )
                
            # Store the collection in session state
            st.session_state.Lab4_vectorDB = collection
            st.success("Vector database created and stored in session state!")
        else:
            st.warning("Please upload exactly 7 PDF files.")

# Function to test the vector database
def test_vector_db():
    if 'Lab4_vectorDB' in st.session_state:
        search_string = st.text_input("Enter a search string:", value="Generative AI")
        if search_string:
            embedding = get_embedding(search_string, engine="text-embedding-ada-002")  # Generate embedding for search
            results = st.session_state.Lab4_vectorDB.query(
                query_embeddings=[embedding], 
                n_results=3
            )
            # Output the ordered list of top 3 returned documents
            st.write("Top 3 documents matching the search:")
            for result in results['metadatas']:
                st.write(result['filename'])
    else:
        st.warning("Vector database not found. Please create it first.")

# Main Streamlit app
st.title("Lab 4: Vector Database with PDF Embeddings")

# Button to trigger the vector database creation
if st.button("Create Vector DB"):
    create_lab4_vector_db()

# Button to test the vector database
if st.button("Test Vector DB"):
    test_vector_db()
