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

def add_to_collection(collection, text, filename):
    openai_client = st.session_state.openai_client
    response = openai_client.embeddings.create(
                input = text,
                model ="text-embedding-3-small")
    embedding = response.data[0].embedding
    collection.add(
        documents = [text],
        ids = [filename],
        embeddings = [embedding]
    )

topic = st.sidebar.selectbox ("Topic", "Text Mining", "GenAI")
openai_client = st.session_state.openai_client
response = openai_client.embeddings.create(
                input = topic,
                model = "text-embedding-3-small")
query_embedding = response.data[0].embedding
results = collection.query(
            query_embeddings = [query_embedding],
            n_results = 3)

for i in range(len(results['documents'][0])):
    doc=results['documents'][0][i]
    doc_id = results['ids'][0][i]
    st.write(f"The following file/syllabus might be helpful: {doc_id}")
