import streamlit as st
import openai
import fitz  # PyMuPDF

# Show title and description.
st.title("📄 Question Answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")

# Validate the API key when it's entered
if openai_api_key:
    try:
        # Test the API key with a simple request
        openai.api_key = openai_api_key
        openai.Model.list()  # A simple API call to validate the key
        st.success("API key is valid! You can now upload a document and ask a question.")
    except Exception as e:
        st.error("Invalid API key. Please check and try again.", icon="🚨")
        st.stop()
else:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
    st.stop()

# Let the user upload a file via `st.file_uploader`.
uploaded_file = st.file_uploader(
    "Upload a document (.txt or .pdf)", type=("txt", "pdf")
)
# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    document = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ''
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

# Handle the file upload and removal
if uploaded_file:
    file_extension = uploaded_file.name.split('.')[-1]
    
    if file_extension == 'txt':
        document = uploaded_file.read().decode()
    elif file_extension == 'pdf':
        document = extract_text_from_pdf(uploaded_file)
    else:
        st.error("Unsupported file type.")
        st.stop()
    
    # Store the document in session state
    st.session_state['document'] = document
else:
    # Clear the document from session state if no file is uploaded
    st.session_state.pop('document', None)



# Ask the user for a question via `st.text_area`.
question = st.text_area(
    "Now ask a question about the document!",
    placeholder="Can you give me a short summary?",
    disabled='document' not in st.session_state,
)

# Generate a response if both the document and question are available
if 'document' in st.session_state and question:
    document = st.session_state['document']
    messages = [
        {
            "role": "user",
            "content": f"Here's a document: {document} \n\n---\n\n {question}",
        }
    ]

    # Generate an answer using the OpenAI API.
    try:
        stream = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # Using the specified LLM model
            messages=messages,
            stream=True,
        )

        # Stream the response to the app using `st.write`.
        for chunk in stream:
            st.write(chunk.choices[0].delta.get("content", ""), end="")
    
    except Exception as e:
        st.error(f"Error generating a response: {str(e)}")