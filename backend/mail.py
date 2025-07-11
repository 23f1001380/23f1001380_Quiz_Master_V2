import smtplib
from email.mime.text import MIMEText


SMTP_HOST = 'localhost'
SMTP_PORT = 1025
FROM_EMAIL = 'admin@quizmaster.com'

def send_mail(to, subject, body):
    """
    Send an email via Mailhog SMTP server.
    """
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = to

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.send_message(msg)
