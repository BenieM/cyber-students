from tornado.web import authenticated

from .auth import AuthHandler

class UserHandler(AuthHandler):

    @authenticated
    def get(self):
        self.set_status(200)
        self.response['email'] = self.current_user['email']
        self.response['displayName'] = self.current_user['display_name']
        self.response['phone'] = self.current_user['phone']
        self.response['disabilities'] = self.current_user['disabilities']
        self.write_json()
