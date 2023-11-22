import random
import ssl
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os

sender_email = os.environ.get('SENDER_EMAIL')
email_port = os.environ.get('EMAIL_PORT')
email_password = os.environ.get('EMAIL_PASSWORD')

def generate_random_authcode():
    return ''.join(random.choices('0123456789', k=6))

def send_email(reciever_email, body):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", email_port, context=context) as server:
        server.login(sender_email, password=email_password)
        server.sendmail(sender_email, reciever_email, body)

def authmail_template(authcode, service_name, reciever_address):
    message = MIMEMultipart('')
    message['Subject'] = f'Here is your login code for {service_name}.'
    message['From'] = sender_email
    message['To'] = reciever_address

    text = f"""\
Your login code is: {authcode}.

If you did not request this code, you can safely ignore this email. However it is possible that your mail-info was leaked, check haveibeenpwned.com for potential pwnages.

This email is sent on behalf of {service_name} by the cultofplaintext."""

    html = f"""\
<html>
    <body>
        <h3>Your login code is:</h3>
        <h1>{authcode}</h1>
        <br>
        <p>If you did not request this code, you can safely ignore this email. However it is possible that your mail-info was leaked, check haveibeenpwned.com for potential pwnages.</p>
        <p>This email is sent on behalf of {service_name} by the cultofplaintext.</p>
    </body>
</html>"""

    message.attach(MIMEText(text, 'plain'))
    message.attach(MIMEText(html, 'html'))

    return message.as_string()