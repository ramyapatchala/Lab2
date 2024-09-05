import streamlit as st
from openai import OpenAI, OpenAIError

# Show title and description.
st.title("📄 Document Question Answering - Q&A")
st.write(
    "Upload a document below and ask a question about it – GPT will answer!"
)

# Use the OpenAI API key stored in Streamlit secrets
openai_api_key = st.secrets['key1']

# Validate the API key from secrets.
if openai_api_key:
    try:
        # Create an OpenAI client using the API key from secrets
        client = OpenAI(api_key=openai_api_key)
        # Try a simple API call to check if the key is valid
        client.models.list()
        st.success("API key is valid!", icon="✅")
    except OpenAIError as e:
        st.error(f"Invalid API key: {e}", icon="❌")
else:
    st.error("API key not found in secrets!", icon="❌")

if openai_api_key and 'client' in locals():
    
    # Sidebar: Provide the user with summary options.
    st.sidebar.header("Summary Options")
    
    summary_option = st.sidebar.radio(
        "Choose how you would like the document to be summarized:",
        options=[
            "Summarize the document in 100 words",
            "Summarize the document in 2 connecting paragraphs",
            "Summarize the document in 5 bullet points"
        ]
    )
    
    # Sidebar: Checkbox for selecting the model
    use_advanced_model = st.sidebar.checkbox("Use Advanced Model")
    
    # Choose model based on the checkbox
    model_choice = "gpt-4o" if use_advanced_model else "gpt-4o-mini"
    
    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .md)", type=("txt", "md")
    )
    
    # Ask the user for a question via `st.text_area`.
    #question = st.text_area(
     #   "Now ask a question about the document!",
      #  placeholder="Can you give me a short summary?",
       # disabled=not uploaded_file,
    #)
    
    if uploaded_file:
        
        # Process the uploaded file and question.
        document = uploaded_file.read().decode()
        
        # Modify the question based on the selected summary option.
        if summary_option == "Summarize the document in 100 words":
            summary_instruction = "Summarize this document in 100 words."
        elif summary_option == "Summarize the document in 2 connecting paragraphs":
            summary_instruction = "Summarize this document in 2 connecting paragraphs."
        else:
            summary_instruction = "Summarize this document in 5 bullet points."
        
        # Combine the document and summary instruction
        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {summary_instruction}",
            }
        ]
        
        # Generate an answer using the OpenAI API with the selected model.
        try:
            stream = client.chat.completions.create(
                model=model_choice,
                messages=messages,
                stream=True,
            )
            
            # Stream the response to the app using `st.write_stream`.
            st.write_stream(stream)
        
        except OpenAIError as e:
            st.error(f"Error generating summary: {e}", icon="❌")
