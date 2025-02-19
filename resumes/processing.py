import pdfplumber
import re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
#from resumes.mailer import send_email  # Import mailer module

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    return text.strip()

def extract_email(text):
    """Extracts the first email found in the resume text."""
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None

def preprocess_text(text):
    """Cleans and normalizes text."""
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return text

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text):
    """Generates an embedding vector for the given text."""
    return model.encode(text, convert_to_numpy=True)

def build_faiss_index(resume_embeddings):
    """Creates FAISS index for similarity search."""
    if resume_embeddings:
        d = len(resume_embeddings[0])
        index = faiss.IndexFlatL2(d)
        index.add(np.array(resume_embeddings))
        return index
    return None