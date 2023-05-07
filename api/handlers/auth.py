from datetime import datetime
from time import mktime
from tornado.gen import coroutine
from config import fernet
from cryptography.fernet import Fernet
from tornado.escape import json_decode, utf8

from .base import BaseHandler

class AuthHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        super(AuthHandler, self).__init__(*args, **kwargs)
        # initialize encryption/decryption key
        self.key = fernet
        self.cipher = Fernet(self.key)

    @coroutine
    def prepare(self):
        super(AuthHandler, self).prepare()

        if self.request.method == 'OPTIONS':
            return

        try:
            token = self.request.headers.get('X-Token')
            if not token:
              raise Exception()
        except:
            self.current_user = None
            self.send_error(400, message='You must provide a token!')
            return

        user = yield self.db.users.find_one({
            'token': token
        }, {
            'email': 1,
            'displayName': 1,
            'expiresIn': 1,
            'password': 1,
            'phone': 1,
            'disabilities': 1
        })

        if user is None:
            # if token is invalid, send error
            self.current_user = None
            self.send_error(403, message='Your token is invalid!')
            return

        current_time = mktime(datetime.now().utctimetuple())
        if current_time > user['expiresIn']:
            self.current_user = None
            self.send_error(403, message='Your token has expired!')
            return
        
        # decrypt user data
        self.current_user = {
            'email': user['email'],
            'display_name': user['displayName'],
            'password': user['password'],
            'phone': self.decrypt(user['phone']),
            'disabilities': self.decrypt(user['disabilities'])
            
        }

 
