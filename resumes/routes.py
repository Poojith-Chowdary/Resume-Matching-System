from flask import Blueprint, request, jsonify
import logging
from PyPDF2 import PdfReader
from resumes.processing import (
    preprocess_text, get_embedding, extract_email, extract_name, filter_resumes_with_llm
)
from resumes.mailer import send_email
import re

resume_bp = Blueprint("resumes", __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

def extract_text_from_pdf(file):
    """Extracts text from a PDF file using PyPDF2."""
    try:
        reader = PdfReader(file)
        return " ".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        logging.error(f"Failed to extract text from PDF: {e}")
        return ""

def extract_details_from_paragraph(paragraph):
    """Extracts role, assignment time, duration, assignment link, and required skills from a single paragraph."""

    patterns = {
        "role": r"(?:role|position)[:\s\-]*([A-Za-z /&]+)(?=[.,\n]|$)",
        "assignment_time": r"(?:assignment time|time)[:\s\-]*([0-9]{1,2}:[0-9]{2}\s*(?:AM|PM|am|pm))",
        "duration": r"(?:duration)[:\s\-]*([0-9]+(?:\.[0-9]+)?\s*(?:minutes?|hours?|days?))",
        "assignment_link": r"(?:assignment link|link)[:\s\-]*(https?://\S+)"
    }

    details = {key: "Not provided" for key in patterns}
    
    for key, pattern in patterns.items():
        match = re.search(pattern, paragraph, re.IGNORECASE)
        if match:
            details[key] = match.group(1).strip()

    # Extract required skills (e.g., Java, SQL, Python)
    skills_pattern = r"(?:skills? required|required skills|skills)[:\s\-]*([A-Za-z0-9, /&]+)(?=[.,\n]|$)"
    skills_match = re.search(skills_pattern, paragraph, re.IGNORECASE)
    details["required_skills"] = skills_match.group(1).strip() if skills_match else "Not provided"

    return details

@resume_bp.errorhandler(500)
def internal_error(error):
    logging.error(f"Server error: {error}")
    return jsonify({"error": "Internal server error occurred"}), 500

@resume_bp.route("/upload_and_match", methods=["POST"])
def upload_and_match():
    """Uploads resumes, extracts details from job description, matches candidates, and sends emails."""
    try:
        files = request.files.getlist("resumes")
        job_description = request.form.get("job_description")

        if not files or not job_description:
            return jsonify({"error": "Resumes and job description are required."}), 400

        details = extract_details_from_paragraph(job_description)

        resumes = []
        for file in files:
            if not file.filename.endswith(".pdf"):
                return jsonify({"error": f"Invalid file format: {file.filename}. Only PDFs are allowed."}), 400

            resume_text = extract_text_from_pdf(file)
            if not resume_text.strip():
                logging.warning(f"No text extracted from {file.filename}. Skipping.")
                continue

            processed_text = preprocess_text(resume_text)
            embedding = get_embedding(processed_text)
            candidate_email = extract_email(resume_text) or "No Email Found"
            candidate_name = extract_name(resume_text) or "Candidate"

            resumes.append({
                "filename": file.filename,
                "text": resume_text,
                "email": candidate_email,
                "name": candidate_name,
                "embedding": embedding
            })

        if not resumes:
            return jsonify({"error": "No valid resumes were processed."}), 400

        shortlisted_resumes = filter_resumes_with_llm(resumes, job_description, threshold=50)
        results = []
        emails_sent = 0

        for candidate in shortlisted_resumes:
            results.append({
                "resume": candidate["filename"],
                "email": candidate["email"],
                "score": candidate["score"],
                "reason": candidate.get("reason", "No reason provided")
            })

            if candidate["email"] != "No Email Found":
                try:
                    send_email(
                        recipient=candidate["email"],
                        candidate_name=candidate["name"],
                        role=details["role"],
                        assignment_time=details["assignment_time"],
                        duration=details["duration"],
                        assignment_link=details["assignment_link"]
                    )
                    emails_sent += 1
                except Exception as e:
                    logging.error(f"Failed to send email to {candidate['email']}: {e}")

        return jsonify({
            "message": "Resumes processed, matched, and emails sent successfully.",
            "matches": results,
            "emails_sent": emails_sent
        })

    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500
