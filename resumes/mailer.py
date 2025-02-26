from flask_mail import Mail, Message

mail = Mail()  # Initialize without 'app'

def init_mail(app):
    mail.init_app(app)

from flask_mail import Mail, Message

mail = Mail()  # Initialize without 'app'

def init_mail(app):
    mail.init_app(app)

def send_email(recipient, candidate_name, role, assignment_time, duration, assignment_link):
    """Sends a detailed email to the shortlisted candidate."""
    subject = f"Congratulations {candidate_name}! You have been shortlisted for the {role} role"
    body = (
        f"Dear {candidate_name},\n\n"
        f"Congratulations! You have been shortlisted for the role of {role}.\n"
        f"Here are the details of your assignment:\n"
        f"- Assignment Time: {assignment_time}\n"
        f"- Duration: {duration}\n"
        f"- Assignment Link: {assignment_link}\n\n"
        "Please complete the assignment within the given timeframe.\n\n"
        "Best regards,\n"
        "HR Team"
    )

    msg = Message(subject, sender="jhondoe7001@gmail.com", recipients=[recipient])
    msg.body = body
    mail.send(msg)
