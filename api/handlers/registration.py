import bcrypt
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.fernet import Fernet
from json import dumps
from logging import info
from tornado.escape import json_decode, utf8
from tornado.gen import coroutine

from .base import BaseHandler
from .config import fernet_key


class RegistrationHandler(BaseHandler):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fernet = Fernet(fernet_key)

    def encrypt_field(self, plaintext):
        """Encrypt a field using Fernet"""
        ciphertext = self.fernet.encrypt(utf8(plaintext))
        return urlsafe_b64encode(ciphertext).decode()

    def decrypt_field(self, ciphertext):
        """Decrypt a field using Fernet"""
        ciphertext = urlsafe_b64decode(ciphertext)
        plaintext = self.fernet.decrypt(ciphertext)
        return plaintext.decode()

    @coroutine
    def post(self):
        try:
            body = json_decode(self.request.body)
            email = body['email'].lower().strip()
            if not isinstance(email, str):
                raise Exception()
            password = body['password']
            if not isinstance(password, str):
                raise Exception()
            display_name = body.get('displayName', email)

            phone = body.get('phone', '')
            if phone is not None and not isinstance(phone, str):
                raise Exception('Phone number must be a string')
            elif not phone:
                raise Exception('Please enter a phone number!')

            disabilities = body.get('disabilities', '')
            if disabilities is not None and not isinstance(disabilities, str):
                raise Exception('Disabilities must be a string')
            elif not disabilities:
                raise Exception('Please enter NA if this field does not apply')
        except Exception as e:
             self.send_error(400, message='You must provide an email address, password, display name, phone, and disabilities')
        
        # Check if user with email already exists
        user = yield self.db.users.find_one({
          'email': email
        }, {})

        if user is not None:
            self.send_error(409, message='A user with the given email address already exists!')
            return

        # Hash the password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        # Encrypt sensitive fields
        phone_encrypted = self.encrypt_field(phone)
        disabilities_encrypted = self.encrypt_field(disabilities)

        # Insert user data into database
        yield self.db.users.insert_one({
            'email': email,
            'password': password_hash,  # store the hashed password
            'displayName': display_name,
            'phone': phone_encrypted,
            'disabilities': disabilities_encrypted
        })

        # Add email/displayname user data to response
        self.response['email'] = email
        self.response['displayName'] = display_name

        self.write_json()
