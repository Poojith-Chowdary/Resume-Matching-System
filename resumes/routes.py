from flask import Blueprint, request, jsonify
import numpy as np
import faiss
from resumes.processing import extract_text_from_pdf, preprocess_text, get_embedding, build_faiss_index, extract_email
from resumes.mailer import send_email

resume_bp = Blueprint("resumes", __name__)

# Global variables to store resume data
resume_embeddings = []
resume_files = []
resume_texts = []
resume_emails = []

@resume_bp.route("/upload_and_match", methods=["POST"])
def upload_and_match():
    """Uploads resumes, processes job description, matches candidates, and sends emails."""
    global resume_embeddings, resume_files, resume_texts, resume_emails
    resume_embeddings.clear()
    resume_files.clear()
    resume_texts.clear()
    resume_emails.clear()

    # Get resumes and job description from request
    files = request.files.getlist("resumes")
    job_description = request.form.get("job_description")

    if not files or not job_description:
        return jsonify({"error": "Both resumes and job description are required"}), 400

    # Process resumes
    for file in files:
        resume_text = extract_text_from_pdf(file)
        processed_text = preprocess_text(resume_text)
        embedding = get_embedding(processed_text)

        candidate_email = extract_email(resume_text)
        resume_emails.append(candidate_email if candidate_email else "No Email Found")
        resume_embeddings.append(embedding)
        resume_files.append(file.filename)
        resume_texts.append(resume_text)

    # Process and match job description
    jd_embedding = get_embedding(preprocess_text(job_description))
    index = build_faiss_index(resume_embeddings)
    if not index:
        return jsonify({"error": "Failed to build FAISS index"}), 400

    D, I = index.search(np.array([jd_embedding]), k=len(resume_files))
    results = []
    shortlisted_emails = []

    for rank, i in enumerate(I[0]):
        if i >= len(resume_files):
            continue

        score = round(float(1 / (1 + D[0][rank])), 2)
        candidate_email = resume_emails[i]
        results.append({"resume": resume_files[i], "email": candidate_email, "score": score})

        if candidate_email != "No Email Found":
            shortlisted_emails.append(candidate_email)

    # Send emails to shortlisted candidates
    if shortlisted_emails:
        subject = "Congratulations! You have been shortlisted"
        body = "Dear Candidate,\n\nYou have been shortlisted for the job. Please stay tuned for further updates.\n\nBest regards,\nHR Team"
        for email in shortlisted_emails:
            send_email(email, subject, body)

    return jsonify({"message": "Resumes processed and matched successfully", "matches": results, "emails_sent": len(shortlisted_emails)})
