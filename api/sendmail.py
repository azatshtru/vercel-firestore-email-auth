from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl

from _firebase import firebase
from _utils import *
from _config import firebase_config, email_config

class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        #send headers
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        #read email from request body
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        kv = dict(parse_qsl(post_body.decode('utf-8')))
        reciever_email = kv['email']

        #generate authcode and store it in firestore under serverauth/{reciever_email} document
        f = firebase(firebase_config=firebase_config())
        authcode = generate_random_authcode()
        token_id = f.generate_auth_id('serveradmin', claims={ 'admin': True })
        f.create_document(id_token=token_id, db_name='dash-12112', collection_path=['serverauth'], 
                        document_id=f'{reciever_email}', data={ 'authcode': authcode })

        #send the authcode to the reciever_email
        service_name = 'discipline observer'
        message = authmail_template(authcode=authcode, service_name=service_name, sender_address=email_config()['sender_email'], reciever_address=reciever_email)
        send_email(emailconfig=email_config(), reciever_email=reciever_email, body=message)

        return