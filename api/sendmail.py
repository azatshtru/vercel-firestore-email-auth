from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl

from api._firebase import firebase
from api._utils import *
from api._config import firebase_config, email_config, AUTHCODE_EXPIRE_MINUTES, AUTHCODE_TRIAL_BUCKET

import json
import time

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        #send headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Access-Control-Expose-Headers', '*')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()

        #read email from request body
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        kv = dict(parse_qsl(post_body.decode('utf-8')))
        if kv.get('email'):
            reciever_email = kv['email']
        else:
            self.wfile.write(json.dumps({"code":"EMLNUL", "description":"invalid or no email recieved"}).encode('utf-8'))
            return

        appcheck_token = self.headers.get('X-Firebase-AppCheck')

        #rate limit if document made less than 5 minutes ago.
        f = firebase(firebase_config=firebase_config(), appcheck_token=appcheck_token)
        token_id = f.generate_auth_id('serveradmin', claims={ 'admin': True })
        doc = f.get_document(id_token=token_id, db_name='dash-12112', collection_path=['serverauth'], document_id=f'{reciever_email}')
        if (doc is not None) and (time.time() - doc['timestamp'] < (AUTHCODE_EXPIRE_MINUTES*60)):
            if kv.get('altdevice'): #send another email with same authcode if different device
                message = authmail_template(authcode=doc['authcode'], service_name='ryth', sender_address=email_config()['sender_email'], reciever_address=reciever_email, expire_minutes=4)
                send_email(emailconfig=email_config(), reciever_email=reciever_email, body=message)
                self.wfile.write(json.dumps({"code":"OK2", "description":"alternate device email sent successfully"}).encode('utf-8'))
                return

            self.wfile.write(json.dumps({"code":"LT5", "description": "server rate limits email sending to 5 minutes."}).encode('utf-8'))
            return

        #generate authcode and store it in firestore under serverauth/{reciever_email} document
        authcode = generate_random_authcode()
        f.delete_document(id_token=token_id, db_name='dash-12112', collection_path=['serverauth'], document_id=f'{reciever_email}')
        f.create_document(id_token=token_id, db_name='dash-12112', collection_path=['serverauth'], document_id=f'{reciever_email}', data={ 'authcode': authcode, 'timestamp': time.time(), 'bucket': AUTHCODE_TRIAL_BUCKET })

        #send the authcode to the reciever_email
        message = authmail_template(authcode=authcode, service_name='ryth', sender_address=email_config()['sender_email'], reciever_address=reciever_email)
        send_email(emailconfig=email_config(), reciever_email=reciever_email, body=message)

        self.wfile.write(json.dumps({"code":"OK1", "description":"email sent successfully"}).encode('utf-8'))
        return
