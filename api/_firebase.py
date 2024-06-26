import requests
import jwt
import time
import json

class firebase():

    def __init__(self, firebase_config, appcheck_token):
        self.api_key = firebase_config['api_key']
        self.service_account_email = firebase_config['service_account_email']
        self.private_key = firebase_config['private_key']
        self.appcheck_token = appcheck_token

    def create_custom_token(self, uid, claims={}):
        payload = {
            "iss": self.service_account_email,
            "sub": self.service_account_email,
            "aud": "https://identitytoolkit.googleapis.com/google.identity.identitytoolkit.v1.IdentityToolkit",
            "iat": time.time(),
            "exp": time.time()+(60*60),
            "uid": uid,
            "claims": claims
        }
        return jwt.encode(payload, self.private_key, algorithm="RS256")

    def generate_auth_id(self, uid, claims={}):
        token = self.create_custom_token(uid, claims=claims)
        binary_data = f'{{"token":"{token}", "returnSecureToken":true}}'
        r = requests.post(
            f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={self.api_key}',
            data=binary_data.encode('utf-8'),
            headers={'Content-type':'application/json', 'X-Firebase-AppCheck':self.appcheck_token}
        )
        response = json.loads(r.text.replace("'", "\""))
        return response['idToken']

    def firestore_parse_data(self, data):
        parsed_data = {}
        for k in data:
            if not isinstance(k, str):
                continue
            if isinstance(data[k], str):
                parsed_data[k] = { "stringValue": data[k] }
            if isinstance(data[k], float):
                parsed_data[k] = { "doubleValue": data[k] }
            if isinstance(data[k], int):
                parsed_data[k] = { "integerValue": data[k] }
        return parsed_data

    def create_document(self, id_token, db_name, collection_path, document_id, data):
        r = requests.post(
            f"https://firestore.googleapis.com/v1/projects/{db_name}/databases/(default)/documents/{'/'.join(collection_path)}?documentId={document_id}&mask.fieldPaths={'&mask.fieldPaths='.join(list(data.keys()))}&key={self.api_key}",
            headers={
                'Authorization': f'Bearer {id_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Firebase-AppCheck': self.appcheck_token
            },
            json={
                "fields": self.firestore_parse_data(data)
            }
        )
        return r.text

    def firestore_deparse_data(self, data):
        deparsed_data = {}
        data = json.loads(data)['fields']
        for k in data:
            if data[k].get('stringValue'):
                deparsed_data[k] = data[k].get('stringValue')
            if data[k].get('doubleValue'):
                deparsed_data[k] = data[k].get('doubleValue')
            if data[k].get('integerValue'):
                deparsed_data[k] = int(data[k].get('integerValue'))
        return deparsed_data

    def get_document(self, id_token, db_name, collection_path, document_id):
        r = requests.get(
            f"https://firestore.googleapis.com/v1/projects/{db_name}/databases/(default)/documents/{'/'.join(collection_path)}/{document_id}?key={self.api_key}",
            headers={
                'Authorization': f'Bearer {id_token}',
                'Accept': 'application/json',
                'X-Firebase-AppCheck': self.appcheck_token
            }
        )
        try:
            return self.firestore_deparse_data(r.text)
        except:
            return None

    def delete_document(self, id_token, db_name, collection_path, document_id):
        r = requests.delete(
            f"https://firestore.googleapis.com/v1/projects/{db_name}/databases/(default)/documents/{'/'.join(collection_path)}/{document_id}?key={self.api_key}",
            headers={
                'Authorization': f'Bearer {id_token}',
                'Accept': 'application/json',
                'X-Firebase-AppCheck': self.appcheck_token
            }
        )

    def update_document(self, id_token, db_name, collection_path, document_id, data):
        r = requests.patch(
            f"https://firestore.googleapis.com/v1/projects/{db_name}/databases/(default)/documents/{'/'.join(collection_path)}/{document_id}?updateMask.fieldPaths={'&updateMask.fieldPaths='.join(list(data.keys()))}&key={self.api_key}",
            headers={
                'Authorization': f'Bearer {id_token}',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Firebase-AppCheck': self.appcheck_token
            },
            json={
                "fields": self.firestore_parse_data(data)
            }
        )
        return r.text