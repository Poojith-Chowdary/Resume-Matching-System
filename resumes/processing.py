import pdfplumber
import re
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from resumes.llm_filter import evaluate_resume_with_llm # Import LLM function

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF file."""
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    return text.strip()

def extract_email(text):
    """Extracts the first email found in the resume text."""
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None

def extract_name(text):
    """
    Extracts the candidate's name from the resume text.
    Assumes the name is at the top or follows common patterns like 'Name:'.
    """
    # Check for patterns like 'Name: John Doe'
    name_match = re.search(r'(?:Name[:\-]?\s*)([A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+)', text)
    if name_match:
        return name_match.group(1)

    # If no pattern matched, try the first line of the resume as a fallback
    lines = text.strip().split('\n')
    if lines and len(lines[0].split()) <= 4:  # Assuming names are usually short
        return lines[0].strip()

    return None

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

def filter_resumes_with_llm(resumes, job_description, threshold=50):
    """
    Uses an LLM to filter resumes based on job relevance.

    Args:
        resumes (list of dict): List of resumes with text, embeddings, and emails.
        job_description (str): The job description.
        threshold (int): Minimum score required to be shortlisted.

    Returns:
        List of shortlisted resumes with LLM scores.
    """
    shortlisted_resumes = []

    for resume in resumes:
        score, reason = evaluate_resume_with_llm(resume["text"], job_description)

        if score >= threshold:
            resume["score"] = score
            resume["reason"] = reason
            shortlisted_resumes.append(resume)

    return shortlisted_resumes