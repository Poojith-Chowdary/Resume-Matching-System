import requests
import re
import os

# API Endpoint and Key
API_URL = "https://open-ai21.p.rapidapi.com/conversationllama"  # Replace with actual API URL
API_KEY = "a991133e21mshc05b33ebc46179fp1b4923jsn421d38661c82"  # Replace with your API key

def evaluate_resume_with_llm(resume_text, job_description):
    """
    Uses an LLM to evaluate how well a resume matches a job description.
    Returns a score (0-100) and a short reason.
    """

    prompt = f"""
    You are an AI assistant for HR recruitment. Evaluate the following resume against the job description. Assign a score from 0 to 100, where 100 indicates an ideal match. Consider these factors:

    - Skill Match (40%)
    - Experience Relevance (30%)
    - Educational Background (20%)
    - Certifications and Projects (10%)

    Resume:
    {resume_text}

    Job Description:
    {job_description}

    Return your evaluation as a JSON object in the following format:
    {{
    "score": <integer from 0 to 100>,
    "reason": "<brief explanation of the score>"
    }}
    """

    payload = {
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "web_access": False
    }


    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "open-ai21.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raises error for bad responses (4xx, 5xx)
        
        # Print full JSON response to debug
        print("Full API Response:", response.json())

        output_text = response.json().get("result", "")
        if not output_text:
            print("No 'result' found in response.")
            return 0, "No response from LLM"

        # Extract score and reason
        score_match = re.search(r"(?i)\"score\"\s*:\s*(\d+)", output_text)
        reason_match = re.search(r"\"reason\"\s*:\s*\"(.*?)\"", output_text)

        score = int(score_match.group(1)) if score_match else 0
        reason = reason_match.group(1).strip() if reason_match else "Reason not provided"

        return score, reason

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return 0, "Error in API request"

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return 0, "Unexpected error occurred"

        