import streamlit as st
import openai
import os
import chromadb
from bs4 import BeautifulSoup
from openai import OpenAI

# Function to verify OpenAI API key
def verify_openai_key(api_key):
    try:
        client = OpenAI(api_key=api_key)
        client.models.list()
        return client, True, "API key is valid"
    except Exception as e:
        return None, False, str(e)

# Vector DB functions
def add_to_collection(collection, text, filename):
    openai_client = OpenAI(api_key=st.secrets['key1'])
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    embedding = response.data[0].embedding
    collection.add(
        documents=[text],
        ids=[filename],
        embeddings=[embedding]
    )
    return collection

# OpenAI function calling setup
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_vectordb",
            "description": "Search the vector database for relevant information about iSchool student organizations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search the vector database."
                    }
                },
                "required": ["query"]
            },
        },
    }
]

# Function for OpenAI chat completion requests
def chat_completion_request(messages, tools):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        return response
    except Exception as e:
        st.error(f"Unable to generate ChatCompletion response. Error: {e}")
        return e

def setup_vectordb():
    db_path = "HW4_VectorDB"
    
    if not os.path.exists(db_path):
        st.info("Setting up vector DB for the first time...")
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_or_create_collection(
            name="HW4Collection",
            metadata={"hnsw:space": "cosine", "hnsw:M": 32}
        )
        
        su_orgs_path = os.path.join(os.getcwd(), "HWs/su_orgs/")
        html_files = [f for f in os.listdir(su_orgs_path) if f.endswith('.html')]
        
        for html_file in html_files:
            file_path = os.path.join(su_orgs_path, html_file)
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                collection = add_to_collection(collection, text, html_file)
        
        st.success(f"VectorDB setup complete with {len(html_files)} HTML files!")
    else:
        st.info("VectorDB already exists. Loading from disk...")
        client = chromadb.PersistentClient(path=db_path)
        st.session_state.HW4_vectorDB = client.get_collection(name="HW4Collection")

def search_vectordb(query, k=3):
    if 'HW4_vectorDB' in st.session_state:
        collection = st.session_state.HW4_vectorDB
        openai_client = OpenAI(api_key=st.secrets['key1'])
        response = openai_client.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        )
        query_embedding = response.data[0].embedding
        results = collection.query(
            query_embeddings=[query_embedding],
            include=['documents', 'distances', 'metadatas'],
            n_results=k
        )
        return results
    else:
        st.error("VectorDB not set up. Please set up the VectorDB first.")
        return None

# Streamlit App
st.title("iSchool Student Organizations Chatbot")

# API key verification
openai_api_key = st.secrets["key1"]
client, is_valid, message = verify_openai_key(openai_api_key)

if is_valid:
    st.sidebar.success(f"OpenAI API key is valid!", icon="✅")
else:
    st.sidebar.error(f"Invalid OpenAI API key: {message}", icon="❌")
    st.stop()

# Set up VectorDB
setup_vectordb()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know about iSchool student organizations?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Query VectorDB for relevant documents
    results = search_vectordb(prompt)
    
    if results:
        context = " ".join([doc for doc in results['documents'][0]])
        context_message = {"role": "system", "content": f"Relevant information: {context}"}
    else:
        context_message = {"role": "system", "content": "No specific context found."}

    messages_for_llm = [context_message, {"role": "user", "content": prompt}]

    # Generate response using OpenAI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        response = chat_completion_request(messages_for_llm, tools=tools)
        assistant_response = response.choices[0].message.content
        message_placeholder.markdown(assistant_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
