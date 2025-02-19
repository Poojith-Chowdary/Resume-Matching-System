from flask_mail import Mail, Message

mail = Mail()  # Initialize without 'app'

def init_mail(app):
    mail.init_app(app)

def send_email(recipient, subject, body):
    """Sends an email using Flask-Mail."""
    msg = Message(subject, sender="jhondoe7001@gmail.com", recipients=[recipient])
    msg.body = body
    mail.send(msg)
