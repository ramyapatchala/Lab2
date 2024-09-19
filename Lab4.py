import streamlit as st
from openai import OpenAI
import os
from PyPDF2 import PdfReader

__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb

if 'openai_client' not in st.session_state:
    api_key = st.secrets['key1']
    st.session_state.openai_client = OpenAI(api_key = api_key)

def create_lab4_vectorDB():
    if 'Lab4_vectorDB' not in st.session_state:
        # Initialize ChromaDB client and collection
        client = chromadb.Client()
        collection = client.create_collection("Lab4Collection")
        
        # OpenAI API setup
        openai_client = st.session_state.openai_client
        
        # Directory containing the 7 PDF files
        pdf_dir = "path_to_pdf_files"  # Update this path to the actual directory of the PDF files
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            file_path = os.path.join(pdf_dir, pdf_file)
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                text = ""
                for page in range(len(reader.pages)):
                    text += reader.pages[page].extract_text()
                
                # Create embeddings using OpenAI model
                response = openai_client.embeddings.create(
                    input=text,
                    model="text-embedding-3-small"
                )
                embedding = response.data[0].embedding
                
                # Add document to ChromaDB collection
                collection.add(
                    documents=[text],
                    ids=[pdf_file],  # Use filename as ID
                    embeddings=[embedding],
                    metadatas=[{"filename": pdf_file}]
                )
        
        # Store the collection in session_state
        st.session_state.Lab4_vectorDB = collection

# Function to search the vectorDB
def search_vectorDB(search_query):
    collection = st.session_state.Lab4_vectorDB
    openai_client = st.session_state.openai_client
    
    # Create embedding for the search query
    response = openai_client.embeddings.create(
        input=search_query,
        model="text-embedding-3-small"
    )
    query_embedding = response.data[0].embedding
    
    # Query the collection with the search string
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
    
    # Display the results (top 3 documents)
    st.write("Top 3 relevant documents:")
    for i in range(len(results['documents'][0])):
        doc_id = results['ids'][0][i]
        st.write(f"- {doc_id}")

# Create vectorDB if not already created
if 'Lab4_vectorDB' not in st.session_state:
    create_lab4_vectorDB()

# Test the vectorDB with a sample search query
search_query = st.sidebar.text_input("Enter search query", "Generative AI")
if st.button("Search"):
    search_vectorDB(search_query)
