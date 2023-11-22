import requests
import jwt
import time
import json
import os

api_key = os.environ.get("FIREBASE_API_KEY")
service_account_email = os.environ.get("FIREBASE_SERVICE_EMAIL")
private_key = os.environ.get("FIREBASE_PRIVATE_KEY")

def create_custom_token(uid, claims={}):
    payload = {
        "iss": service_account_email,
        "sub": service_account_email,
        "aud": "https://identitytoolkit.googleapis.com/google.identitytoolkit.v1.IdentityToolkit",
        "iat": time.time(),
        "exp": time.time()+(60*60),
        "uid": uid,
        "claims": claims
    }
    return jwt.encode(payload, private_key, algorithm="RS256")

def generate_auth_id(uid, claims={}):
    token = create_custom_token(uid, claims=claims)
    binary_data = f'{{"token":"{token}", "returnSecureToken":true}}'
    r = requests.post(
        f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}',
        data=binary_data,
        headers={'Content-type':'application/json'}
    )
    response = json.loads(r.text.replace("'", "\""))
    return response['idToken']

def firestore_parse_data(data):
    parsed_data = {}
    for k in data:
        if not isinstance(k, str):
            continue
        if isinstance(data[k], str):
            parsed_data[k] = { "stringValue": data[k] }
    return parsed_data

def create_document(id_token, db_name, collection_path, document_id, data):
    r = requests.post(
        f"https://firestore.googleapis.com/v1/projects/{db_name}/databases/(default)/documents/{'/'.join(collection_path)}?documentId={document_id}&mask.fieldPaths={'&mask.fieldPaths='.join(list(data.keys()))}&key={api_key}",
        headers={
            'Authorization': f'Bearer {id_token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        json={
            "fields": firestore_parse_data(data)
        }
    )
    return r.text