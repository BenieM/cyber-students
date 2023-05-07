from json import dumps
from logging import info
from tornado.escape import json_decode, utf8
from tornado.gen import coroutine

from .base import BaseHandler


class RegistrationHandler(BaseHandler):

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
            if not isinstance(display_name, str):
                raise Exception()

            phone = body.get('phone')
            if phone is not None and not isinstance(phone, str):
                raise Exception('Phone number must be a string')
            elif phone is None:
                raise Exception('Please enter a phone number!')
            
            disabilities = body.get('disabilities')
            if disabilities is not None and not isinstance(disabilities, str):
                raise Exception('Disabilities must be a string')
            elif disabilities is None:
                raise Exception('Please enter NA if this field does not apply')
        except Exception as e:
            self.send_error(400, message=str(e))
            return

        if not email:
            self.send_error(400, message='The email address is invalid!')
            return

        if not password:
            self.send_error(400, message='The password is invalid!')
            return

        if not display_name:
            self.send_error(400, message='The display name is invalid!')
            return
        
        user = yield self.db.users.find_one({
          'email': email
        }, {})

        if user is not None:
            self.send_error(409, message='A user with the given email address already exists!')
            return

        yield self.db.users.insert_one({
            'email': email,
            'password': password,
            'displayName': display_name,
            'phone': phone,
            'disabilities': disabilities
        })

        self.response['email'] = email
        self.response['displayName'] = display_name
        self.response['phone'] = phone
        self.response['disabilities'] = disabilities

        self.write_json()
