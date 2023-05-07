from tornado.web import authenticated

from .auth import AuthHandler


class UserHandler(AuthHandler):

    @authenticated
    async def get(self):
        # Get the current user's id
        user_id = self.current_user['_id']
        # Query the database for the user with the given id
        user = await self.db.users.find_one({'_id': user_id}, {})
        # If user is not found, return 404 error
        if user is None:
            self.send_error(404, message='User not found')
            return
        # Set the HTTP status code to 200 (OK)
        self.set_status(200)
        # Decrypt the user's email, display name, phone number, and disabilities
        self.response['email'] = self.decrypt_field(user['email'])
        self.response['displayName'] = self.decrypt_field(user['display_name'])
        self.response['phone'] = self.decrypt_field(user['phone'])
        self.response['disabilities'] = self.decrypt_field(user['disabilities'])
        self.write_json()
