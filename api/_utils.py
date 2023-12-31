import random
import ssl
import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_random_authcode():
    return ''.join(random.choices('0123456789', k=6))

def send_email(emailconfig, reciever_email, body):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", emailconfig['port'], context=context) as server:
        server.login(emailconfig['sender_email'], password=emailconfig['password'])
        server.sendmail(emailconfig['sender_email'], reciever_email, body)

def authmail_template(authcode, service_name, sender_address, reciever_address, expire_minutes=5):
    message = MIMEMultipart('alternative')
    message['Subject'] = f'Here is your login code for {service_name}.'
    message['From'] = sender_address
    message['To'] = reciever_address

    text = f"""\
Your login code is: {authcode}.

This login code expires in {expire_minutes} minutes.

This email is sent by thecultofplaintext on behalf of {service_name}.

If you did not request this code, you can safely ignore this email. However it is possible that your mail-info was leaked, check haveibeenpwned.com for potential pwnages."""

    html = f"""\
<html>
    <body>
        <h3>Your login code is:</h3>
        <h1>{authcode}</h1>
        <p>This login code expires in {expire_minutes} minutes.</p>
        <br>
        <p>This email is sent by thecultofplaintext on behalf of {service_name}.</p>
        <br>
        <p>If you did not request this code, you can safely ignore this email. However it is possible that your mail-info was leaked, check haveibeenpwned.com for potential pwnages.</p>
    </body>
</html>"""

    message.attach(MIMEText(text, 'plain'))
    message.attach(MIMEText(html, 'html'))

    return message.as_string()
