from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl

from api._firebase import firebase
from api._config import firebase_config, AUTHCODE_EXPIRE_MINUTES

import json
import time

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        #send headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'X-Firebase-AppCheck')
        self.end_headers()

        #read authcode from request body
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        kv = dict(parse_qsl(post_body.decode('utf-8')))
        authcode = kv['authcode']
        reciever_email = kv['email']

        appcheck_token = self.headers.get('X-Firebase-AppCheck')

        #read stored authcode from firestore
        f = firebase(firebase_config=firebase_config(), appcheck_token=appcheck_token)
        token_id = f.generate_auth_id('serveradmin', claims={ 'admin': True })
        doc = f.get_document(id_token=token_id, db_name='dash-12112', collection_path=['serverauth'], document_id=f'{reciever_email}')

        if not doc:
            self.wfile.write(json.dumps({"error":"ERRN0F", "description":"no associated auth entry found. (n0f)"}).encode('utf-8'))
            return

        #check if email code is expired
        if (time.time() - doc['timestamp']) > (AUTHCODE_EXPIRE_MINUTES+AUTHCODE_EXPIRE_MINUTES+2)*60:
            self.wfile.write(json.dumps({"error":"ERRE4E", "description":"recieved code was expired (e4e)"}).encode('utf-8'))
            return

        #check if stored authcode matches the request's authcode
        if authcode == str(doc['authcode']):
            user_token = f.create_custom_token(reciever_email)
            self.wfile.write(json.dumps({"token":user_token}).encode('utf-8'))
        else:
            #check if wrong authcode entered multiple times in a row
            bucket = doc['bucket']
            if bucket < 1:
                f.delete_document(id_token=token_id, db_name='dash-12112', collection_path=['serverauth'], document_id=f'{reciever_email}')
                self.wfile.write(json.dumps({"error":"ERRIXT", "description":"recieved code was incorrect multiple times in a row. (ixt)"}).encode('utf-8'))
                return
            f.update_document(id_token=token_id, db_name='dash-12112', collection_path=['serverauth'], document_id=f'{reciever_email}', data={ 'bucket': int(bucket)-1 })
            self.wfile.write(json.dumps({"error":"ERRI7T", "description":"recieved code was incorrect (i7t)"}).encode('utf-8'))

        return
