from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl

from _firebase import firebase
from _utils import *
from _config import firebase_config, email_config, AUTHCODE_EXPIRE_MINUTES

import time

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        #send headers
        self.send_response(200)
        self.send_header('Content-length', 0)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        #read email from request body
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        kv = dict(parse_qsl(post_body.decode('utf-8')))
        reciever_email = kv['email']

        #generate authcode and store it in firestore under serverauth/{reciever_email} document
        f = firebase(firebase_config=firebase_config())
        token_id = f.generate_auth_id('serveradmin', claims={ 'admin': True })
        doc = f.get_document(id_token=token_id, db_name='dash-12112', collection_path=['serverauth'], document_id=f'{reciever_email}')
        if (doc is not None) and (time.time() - doc['timestamp'] < (AUTHCODE_EXPIRE_MINUTES*60)):
            return
        authcode = generate_random_authcode()
        f.delete_document(id_token=token_id, db_name='dash-12112', collection_path=['serverauth'], document_id=f'{reciever_email}')
        f.create_document(id_token=token_id, db_name='dash-12112', collection_path=['serverauth'], document_id=f'{reciever_email}', data={ 'authcode': authcode, 'timestamp': time.time() })

        #send the authcode to the reciever_email
        service_name = 'ryth'
        message = authmail_template(authcode=authcode, service_name=service_name, sender_address=email_config()['sender_email'], reciever_address=reciever_email)
        send_email(emailconfig=email_config(), reciever_email=reciever_email, body=message)

        return
