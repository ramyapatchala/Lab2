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

def setup_vectordb():
    if 'vectordb_collection' not in st.session_state:
        client = chromadb.PersistentClient()
        collection = client.get_or_create_collection("PDFCollection")
        
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
        
        st.session_state.vectordb_collection = collection
        st.success(f"VectorDB setup complete with {len(pdf_files)} PDF files!")
    else:
        st.info("VectorDB already set up.")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def rerank_results(query_embedding, results, n_results=3):
    similarities = [cosine_similarity(query_embedding, result) for result in results['embeddings'][0]]
    sorted_indices = np.argsort(similarities)[::-1]
    return {
        'ids': [[results['ids'][0][i] for i in sorted_indices[:n_results]]],
        'documents': [[results['documents'][0][i] for i in sorted_indices[:n_results]]],
        'embeddings': [[results['embeddings'][0][i] for i in sorted_indices[:n_results]]]
    }

# Streamlit app
st.title("Improved PDF Reader and VectorDB Demo")

# Setup VectorDB button
if st.button("Setup VectorDB"):
    setup_vectordb()

# Topic selection and query
topic = st.sidebar.selectbox("Topic", ("Text Mining", "Generative AI and its applications"))
if st.sidebar.button("Search"):
    if 'vectordb_collection' in st.session_state:
        collection = st.session_state.vectordb_collection
        openai_client = st.session_state.openai_client
        
        # Create a more specific query
        if topic == "Generative AI and its applications":
            query = "Generative AI technologies, applications, and impact in various fields"
        else:
            query = topic
        
        response = openai_client.embeddings.create(
                        input=query,
                        model="text-embedding-3-small")
        query_embedding = response.data[0].embedding
        
        # Fetch more results initially
        results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=10)
        
        # Rerank the results
        reranked_results = rerank_results(query_embedding, results)
        
        for i in range(len(reranked_results['ids'][0])):
            doc_id = reranked_results['ids'][0][i]
            doc_text = reranked_results['documents'][0][i][:200]  # Display first 200 characters
            st.write(f"File: {doc_id}")
            st.write(f"Preview: {doc_text}...")
            st.write("---")
    else:
        st.error("VectorDB not set up. Please set up the VectorDB first.")
