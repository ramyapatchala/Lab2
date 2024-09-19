import streamlit as st
from openai import OpenAI
import os
from PyPDF2 import PdfReader
import importlib
importlib.import_module('pysqlite3')
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

def setup_vectordb():
    if 'Lab4_vectorDB' not in st.session_state:
        client = chromadb.Client()
        collection = client.create_collection("Lab4Collection")
        
        # Get list of PDF files from datafiles folder
        datafiles_path = os.path.join(os.getcwd(), "datafiles")
        pdf_files = [f for f in os.listdir(datafiles_path) if f.endswith('.pdf')]
        
        for pdf_file in pdf_files:
            file_path = os.path.join(datafiles_path, pdf_file)
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                add_to_collection(collection, text, pdf_file)
        
        st.session_state.Lab4_vectorDB = collection
        st.success(f"VectorDB setup complete with {len(pdf_files)} PDF files!")
    else:
        st.info("VectorDB already set up.")

def test_vectordb(query):
    if 'Lab4_vectorDB' in st.session_state:
        collection = st.session_state.Lab4_vectorDB
        openai_client = st.session_state.openai_client
        response = openai_client.embeddings.create(
                        input=query,
                        model="text-embedding-3-small")
        query_embedding = response.data[0].embedding
        results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=3)
        
        st.write(f"Top 3 documents for query '{query}':")
        for i, doc_id in enumerate(results['ids'][0], 1):
            st.write(f"{i}. {doc_id}")
    else:
        st.error("VectorDB not set up. Please set up the VectorDB first.")

# Streamlit app
st.title("Lab 4 VectorDB Demo")

# Setup VectorDB button
if st.button("Setup VectorDB"):
    setup_vectordb()

# Test VectorDB
test_query = st.selectbox("Select a test query:", ["Generative AI", "Text Mining", "Data Science Overview"])
if st.button("Test VectorDB"):
    test_vectordb(test_query)

# Original topic selection and query
topic = st.sidebar.selectbox("Topic", ("Text Mining", "GenAI"))
if st.sidebar.button("Search"):
    if 'Lab4_vectorDB' in st.session_state:
        collection = st.session_state.Lab4_vectorDB
        openai_client = st.session_state.openai_client
        response = openai_client.embeddings.create(
                        input=topic,
                        model="text-embedding-3-small")
        query_embedding = response.data[0].embedding
        results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=3)
        for i in range(len(results['documents'][0])):
            doc_id = results['ids'][0][i]
            st.write(f"The following file/syllabus might be helpful: {doc_id}")
    else:
        st.error("VectorDB not set up. Please set up the VectorDB first.")
