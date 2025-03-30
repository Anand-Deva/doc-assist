from document_handler import run_llm
import streamlit as st
import tempfile
import os
import shutil
import openai
import re

# Set page to wide mode
st.set_page_config(layout="wide")

# Custom CSS to style the input border color
st.markdown("""
    <style>
    /* Style the input border */
    .stTextInput input {
        border-color: #FFD700 !important;
        border-width: 2px !important;
    }
    
    /* Style the input border on focus */
    .stTextInput input:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 0 0.2rem rgba(255, 215, 0, 0.25) !important;
    }
    </style>
""", unsafe_allow_html=True)

st.header("Langchain Document Helper Bot")

# Initialize session states
if "user_prompt_history" not in st.session_state:
    st.session_state['user_prompt_history'] = []
if "chat_answers_history" not in st.session_state:
    st.session_state['chat_answers_history'] = []
if "chat_history" not in st.session_state:
    st.session_state['chat_history'] = []
if "current_document" not in st.session_state:
    st.session_state['current_document'] = None
if "openai_api_key" not in st.session_state:
    st.session_state['openai_api_key'] = None
if "api_key_validated" not in st.session_state:
    st.session_state['api_key_validated'] = False

# Get upload directory from environment or use default
UPLOAD_DIR = os.getenv('UPLOAD_DIR', os.path.join(os.getcwd(), 'data', 'uploads'))

# Ensure upload directory exists with proper permissions
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except OSError as e:
    st.error(f"Error creating upload directory: {e}")
    st.stop()

def validate_api_key(api_key: str) -> bool:
    """Validate the OpenAI API key."""
    if not api_key.startswith('sk-') or len(api_key) < 40:
        return False
    
    try:
        # Configure the client
        openai.api_key = api_key
        # Make a minimal API call to validate the key
        openai.models.list()
        return True
    except Exception as e:
        st.error(f"API Key validation error: {str(e)}")
        return False

def save_uploaded_file(uploaded_file):
    """Safely save an uploaded file and return the path."""
    try:
        # Create a unique filename to avoid conflicts
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        
        # Save the uploaded file
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getvalue())
        
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {str(e)}")
        return None

# Function to clear API key
def clear_api_key():
    st.session_state['openai_api_key'] = None
    st.session_state['api_key_validated'] = False
    if 'api_key_input' in st.session_state:
        st.session_state['api_key_input'] = ""

# Create two columns for API key input
api_col1, api_col2 = st.columns([2, 1])

with api_col1:
    api_key = st.text_input(
        "Enter your OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Get your API key from https://platform.openai.com/account/api-keys",
        key="api_key_input"
    )

    if api_key:
        if validate_api_key(api_key):
            st.session_state['openai_api_key'] = api_key
            st.session_state['api_key_validated'] = True
        else:
            st.error("Invalid API key. Please check your API key and try again.")
            st.session_state['api_key_validated'] = False
            st.session_state['openai_api_key'] = None
        
with api_col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
    st.button("Clear API Key", on_click=clear_api_key, key="clear_api_key")

# Show API status
if st.session_state['api_key_validated']:
    st.success("API Key validated and set successfully!")
else:
    st.warning("Please enter a valid OpenAI API key to continue")

# File uploader - only show if API key is validated
if st.session_state['api_key_validated']:
    uploaded_file = st.file_uploader("Upload a PDF document", type=['pdf'])

    # Handle file upload
    if uploaded_file is not None:
        file_path = save_uploaded_file(uploaded_file)
        if file_path:
            st.session_state['current_document'] = file_path
            st.success("Document uploaded successfully!")

# Display chat history
if st.session_state['chat_answers_history']:
    for generated_response, user_query in zip(st.session_state['chat_answers_history'],st.session_state['user_prompt_history']):
        st.chat_message('user').write(user_query)
        st.chat_message('bot').write(generated_response)

# Add some spacing before the prompt input
st.markdown("<br>" * 2, unsafe_allow_html=True)

# Create a container for the prompt input at the bottom
with st.container():
    # Add a horizontal line for visual separation
    st.markdown("---")
    
    # Create a two-column layout for the prompt input
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Handle prompt submission
        def handle_prompt_submit():
            if st.session_state.prompt_input:
                if not st.session_state['api_key_validated']:
                    st.error("Please enter a valid OpenAI API key first!")
                elif st.session_state['current_document'] is None:
                    st.error("Please upload a document first!")
                else:
                    with st.spinner("Generating response..."):
                        prompt = st.session_state.prompt_input
                        try:
                            generated_response = run_llm(
                                prompt, 
                                st.session_state['current_document'], 
                                chat_history=st.session_state['chat_history'],
                                api_key=st.session_state['openai_api_key']
                            )

                            # Store only the response without sources
                            response_text = generated_response['result']

                            st.session_state['user_prompt_history'].append(prompt)
                            st.session_state['chat_answers_history'].append(response_text)
                            st.session_state['chat_history'].append(("human",prompt))
                            st.session_state['chat_history'].append(("ai",response_text))
                            
                            # Clear the input after successful submission
                            st.session_state.prompt_input = ""
                        except Exception as e:
                            st.error(f"Error generating response: {str(e)}")

        # Create the text input with a callback
        st.text_input("Ask a question about your document", 
                     placeholder="Enter your prompt here...",
                     key="prompt_input",
                     on_change=handle_prompt_submit)

# Cleanup function for uploaded files
def cleanup_uploaded_files():
    try:
        if os.path.exists(UPLOAD_DIR):
            for file in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    st.error(f"Error deleting file {file_path}: {e}")
    except Exception as e:
        st.error(f"Error during cleanup: {e}")

# Register cleanup function
import atexit
atexit.register(cleanup_uploaded_files)
        