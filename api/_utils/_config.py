import os

AUTHCODE_EXPIRE_MINUTES = 5

def firebase_config():
    return {
        'api_key': os.environ.get("FIREBASE_API_KEY"),
        'service_account_email': os.environ.get("FIREBASE_SERVICE_EMAIL"),
        'private_key': os.environ.get("FIREBASE_PRIVATE_KEY"),
    }

def email_config():
    return {
        'sender_email': os.environ.get('SENDER_EMAIL'),
        'port': os.environ.get('EMAIL_PORT'),
        'password': os.environ.get('EMAIL_PASSWORD'),
    }