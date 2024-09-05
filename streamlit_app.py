import streamlit as st
import openai
import fitz  # PyMuPDF for reading PDF files

# Function to read PDF files
def read_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Show title and description.
st.title("📄 Document question answering (HW1)")
st.write(
    "Upload a .txt or .pdf document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Set the OpenAI API key
    openai.api_key = openai_api_key

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader("Upload a document (.txt or .pdf)", type=("txt", "pdf"))

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:
        # Process the uploaded file and question.
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension == 'txt':
            document = uploaded_file.read().decode('utf-8')
        elif file_extension == 'pdf':
            document = read_pdf(uploaded_file)
        else:
            st.error("Unsupported file type.")
            st.stop()  # Stop further execution if the file type is invalid

        # Prepare the messages for the ChatCompletion
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": f"Here's a document: {document}\n\n---\n\n{question}"
            }
        ]

        try:
            # Generate an answer using the OpenAI API with the correct method
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # You can use GPT-4 if you have access
                messages=messages
            )

            # Display the result
            answer = response['choices'][0]['message']['content']
            st.write("### Answer:")
            st.write(answer)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    # If the file is removed, stop accessing the data
    if not uploaded_file:
        st.warning("No file uploaded yet or file removed. Upload a file to continue.")
