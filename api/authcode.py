from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl

from _firebase import firebase
from _config import firebase_config

import json

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        #send headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        #read authcode from request body
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        kv = dict(parse_qsl(post_body.decode('utf-8')))
        authcode = kv['authcode']
        reciever_email = kv['email']

        #read stored authcode from firestore
        f = firebase(firebase_config=firebase_config())
        token_id = f.generate_auth_id('serveradmin', claims={ 'admin': True })
        doc = f.get_document(id_token=token_id, db_name='dash-12112', collection_path=['serverauth'], document_id=f'{reciever_email}')
        
        #check if stored authcode matches the request's authcode
        if authcode == str(doc['authcode']):
            f.delete_document(token_id, 'dash-12112', ['serverauth'], document_id=f'{reciever_email}')
            user_token = f.generate_auth_id(reciever_email)
            self.wfile.write(json.dumps(user_token))
        
        return