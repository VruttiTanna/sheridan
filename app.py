import streamlit as st
import io
import PyPDF2
import openai
from PIL import Image
import base64
import os

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
# Set OpenAI API key
#from dotenv import load_dotenv
#load_dotenv()  # This will read the .env file

#openai.api_key = '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'
#openai.api_key = os.getenv("OPENAI_API_KEY")
#openai.api_key=st.secrets["api"]
openai_client = openai.Client(api_key=os.environ.get("OPENAI_API_KEY"))


# Load Sheridan logo
logo = Image.open("sheridan_logo_2.png")

# Function to convert image to base64
def logo_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str

# Streamlit app configuration
st.set_page_config(page_title="PDF Q&A with AI", layout="wide")

# Custom CSS Styling for compact, single-page layout
st.markdown("""
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #e0f2f1;
        }
        .header {
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #1e88e5;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .header img {
            width: 100px;
            height: auto;
            margin-right: 10px;
        }
        .title {
            font-size: 24px;
            color: white;
            font-weight: bold;
        }
        .compact-box {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            margin-bottom: 10px;
        }
        .side-info {
            font-size: 12px;
            color: #888888;
            margin: 10px 0;
        }
        .button {
            font-size: 16px;
            padding: 8px 15px;
            background-color: #1e88e5;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .button:hover {
            background-color: #1565c0;
        }
        .footer {
            background-color: #1e88e5;
            color: white;
            padding: 15px;
            text-align: center;
            border-radius: 8px;
            margin-top: 10px;
        }
        .footer p {
            margin: 0;
            font-size: 12px;
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
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    st.markdown("""
    <div class="side-info">
        <h4>Need Help?</h4>
        <p>Explore FAQs or reach out to support for assistance with using the app.</p>
    </div>
    <div class="side-info">
        <h4>About this App</h4>
        <p>This tool lets you ask questions and summarize PDF content with AI. It's powered by OpenAI’s GPT technology.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="compact-box">
        <h3>Upload your PDF and ask questions!</h3>
        <p>Get insights by asking questions or requesting summaries. This app uses AI to interact with PDF content.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf", label_visibility="collapsed", key="uploader")

    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            pdf_text = extract_text_from_pdf(uploaded_file)
            st.success("PDF text extracted successfully!")

        chunks = split_text(pdf_text)
        question = st.text_input("Enter your question:")

        if question:
            if question.lower() in ["summarize", "summarise"]:
                with st.spinner("Generating summary..."):
                    summary_text = " ".join([summarize_with_openai(chunk) for chunk in chunks])
                    st.write("**Summary:**", summary_text.strip())
            else:
                with st.spinner("Finding the best answer..."):
                    answer = answer_question_with_openai(question, pdf_text)
                    st.write("**Answer:**", answer)

with col3:
    st.markdown("""
    ### Contributors
    - Vrutti Tanna
    - Serageldin Abdelmoaty
    - Mohammad Amir
    """)

# Footer
st.markdown("""
    <div class="footer">
        <p>© 2024 Sheridan College - PDF Q&A Application | Created by the AI Lab</p>
    </div>
""", unsafe_allow_html=True)
