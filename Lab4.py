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
    st.session_state.openai_client = OpenAI(api_key=api_key)

def add_to_collection(collection, text, filename):
    openai_client = st.session_state.openai_client
    response = openai_client.embeddings.create(
                input=text,
                model="text-embedding-3-small")
    embedding = response.data[0].embedding
    collection.add(
        documents=[text],
        ids=[filename],
        embeddings=[embedding]
    )
    return collection

def setup_vectordb():
    if 'vectordb_collection' not in st.session_state:
        client = chromadb.PersistentClient()
        collection = client.get_or_create_collection(name = "PDFCollection")
        
        datafiles_path = os.path.join(os.getcwd(), "datafiles")
        pdf_files = [f for f in os.listdir(datafiles_path) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            file_path = os.path.join(datafiles_path, pdf_file)
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                collection = add_to_collection(collection, text, pdf_file)
        
        st.session_state.vectordb_collection = collection
        st.success(f"VectorDB setup complete with {len(pdf_files)} PDF files!")
    else:
        st.info("VectorDB already set up.")

# Streamlit app
st.title("PDF Reader and VectorDB Demo")

# Setup VectorDB button
if st.button("Setup VectorDB"):
    setup_vectordb()

# Topic selection and query
topic = st.sidebar.selectbox("Topic", ("Text Mining", "OpenAI", "Data Science Overview"))
if st.sidebar.button("Search"):
    if 'vectordb_collection' in st.session_state:
        collection = st.session_state.vectordb_collection
        openai_client = st.session_state.openai_client
        response = openai_client.embeddings.create(
                        input=topic,
                        model="text-embedding-3-small")
        query_embedding = response.data[0].embedding
        results = collection.query(
                    query_embeddings=[query_embedding],
                    include = ['documents', 'distances', 'metadatas'],
                    n_results=3)
        for i in range(len(results['ids'][0])):
            doc_id = results['ids'][0][i]
            dis_id = results['distances'][0][i]
            
            st.write(f"The following file/syllabus might be helpful: {doc_id}")
            st.write(f"distance: {dis_id}")


    else:
        st.error("VectorDB not set up. Please set up the VectorDB first.")
