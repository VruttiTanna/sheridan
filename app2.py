import streamlit as st
import io
import PyPDF2
import openai
from PIL import Image
import base64

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
    text = "".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    return text

# Function to split text into manageable chunks for summarization
def split_text(text, max_length=1000):
    words = text.split()
    chunks, current_chunk, current_length = [], [], 0
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if current_length > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk, current_length = [], 0
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

# OpenAI summarization and Q&A function
def summarize_with_openai(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Summarize the following content."},
                  {"role": "user", "content": text}]
    )
    return response['choices'][0]['message']['content']

def answer_question_with_openai(question, context):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "Answer questions based on provided context."},
                  {"role": "user", "content": f"Context: {context}"},
                  {"role": "user", "content": question}]
    )
    return response['choices'][0]['message']['content']

# Set OpenAI API key
openai.api_key = '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'

# Load Sheridan logo
logo = Image.open("sheridan_logo_2.png")

# Function to convert image to base64
def logo_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

# Streamlit app configuration
st.set_page_config(page_title="PDF Q&A with AI", layout="centered")

# Custom CSS Styling with footer and updated background color
st.markdown("""
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #e0f2f1; /* Light teal for contrast with dark blue logo */
        }
        .header {
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #1e88e5;  /* Light blue for better contrast */
            padding: 20px;
            border-radius: 8px;
            top : 0;
            margin-bottom: 5px;
        }
        .header img {
            width: 120px;
            height: auto;
            margin-right: 10px;
        }
        .title {
            font-size: 28px;
            color: white;
            font-weight: bold;
        }
        .content-box {
            background-color: #ffffff;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .upload-section {
            margin-top: 15px;
        }
        .side-info {
            font-size: 14px;
            color: #888888;
            margin: 10px 0;
        }
        .stFileUploader button {
            background-color: #1e88e5;
            color: white;
            font-size: 16px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .stFileUploader button:hover {
            background-color: #1565c0;
        }
        .button {
            font-size: 18px;
            padding: 10px 20px;
            background-color: #1e88e5;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .button:hover {
            background-color: #1565c0;
        }
        h3 {
            color: #1e88e5;
        }
        .footer {
            background-color: #1e88e5;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px;
            margin-top: 30px;
        }
        .footer p {
            margin: 0;
            font-size: 14px;
        }
    </style>
""", unsafe_allow_html=True)



# Header with logo and title
st.markdown(f"""
    <div class="header">
        <img src="data:image/png;base64,{logo_to_base64(logo)}" alt="Sheridan Logo">
        <div class="title">Sheridan PDF Q&A Application</div>
    </div>
""", unsafe_allow_html=True)

# Side information for left and right panes
st.sidebar.write("""
    <div class="side-info">
        <h4>Need Help?</h4>
        <p>Explore FAQs or reach out to support for assistance with using the app.</p>
    </div>
    <div class="side-info">
        <h4>About this App</h4>
        <p>This tool lets you ask questions and summarize PDF content with AI. It's powered by OpenAI’s GPT technology.</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar content for contributors
st.sidebar.markdown("""
    ### Contributors
    - Vrutti Tanna
""")

# Information Box
st.markdown("""
    <div class="content-box">
        <h3>Upload your PDF file and ask questions based on its content!</h3>
        <p>Get insights from your PDFs by asking targeted questions or requesting summaries. This app uses AI to answer questions based on the uploaded PDF content.</p>
    </div>
""", unsafe_allow_html=True)

# Upload PDF file
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf", label_visibility="collapsed", key="uploader")

# Extract text and prepare Q&A section if file is uploaded
if uploaded_file:
    # Extract text from PDF
    with st.spinner("Extracting text from PDF..."):
        pdf_text = extract_text_from_pdf(uploaded_file)
        st.success("PDF text extracted successfully!")

    # Split text for summarization
    chunks = split_text(pdf_text)

    # User question input
    question = st.text_input("Enter your question:")

    # Answer or Summarize
    if question:
        if question.lower() in ["summarize", "summarise"]:
            with st.spinner("Generating summary..."):
                summary_text = " ".join([summarize_with_openai(chunk) for chunk in chunks])
                st.write("**Summary:**", summary_text.strip())
        else:
            with st.spinner("Finding the best answer..."):
                answer = answer_question_with_openai(question, pdf_text)
                st.write("**Answer:**", answer)

# Footer
st.markdown("""
    <div class="footer">
        <p>© 2024 Sheridan College - PDF Q&A Application | Created by the AI Lab</p>
    </div>
""", unsafe_allow_html=True)
