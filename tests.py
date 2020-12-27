import unittest
import json

from flask import jsonify

from transactions import app, db, routes
from transactions.models import *


class BasicTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        # _app - для зручності, для того, щоб явно бачити, що це не просто app, який імпортований
        self._app = app.test_client()
        self.bytes_to_json_token = ""

    def tearDown(self):
        pass

    def test_home(self):
        response = self._app.get('/')
        self.assertEqual(200, response.status_code)

    def test_hello(self):
        response = self._app.get('/api/v1/hello-world-1')
        print(response)
        headers = {"Content-Type": "text/html; charset=utf-8"}
        self.assertEqual(headers['Content-Type'], response.headers['content-type'])

    def test_create_user(self):
        firstname = "test_user2"
        lastname = "lastname_test2"
        email = "test2@test.com"
        password = "test_pass2"

        # user_data = json.dumps({
        #     "firstname": firstname,
        #     "lastname": lastname,
        #     "email": email,
        #     "password": password
        # })
        # print(user_data)
        response = self._app.post('/user', headers={"Content-Type": "multipart/form-data"},
                                  data={"firstname": "test_user2", "lastname": "lastname_test2",
                                        "email": "test2@test.com", "password": "test_pass2"})
        print(response)
        print(User.query.all())
        if not User.query.filter_by(email='test2@test.com').first:
            self.assertEqual(201, response.status_code)
        else:
            self.assertEqual(403, response.status_code)

    def test_auth(self):
        email = "test2@test.com"
        password = "test_pass2"

        user_data = json.dumps({
            "email": email,
            "password": password
        })

        response = self._app.post('/authentification', headers={"Content-Type": "multipart/form-data"},
                                  data={"email": "test2@test.com", "password": "test_pass2"})

        bytes_response = response.data.decode('utf-8').replace("'", '"')
        self.bytes_to_json_token = json.loads(bytes_response)['token']

    def test_print_token(self):
        pass
        # self.test_auth()

    def test_auth_get_user(self):
        self.test_auth()
        res = User.query.filter_by(email='test2@test.com').first()
        # print(res)
        # print(self.bytes_to_json_token)
        response = self._app.get('/user/test2@test.com', headers={"token": self.bytes_to_json_token})  # or 403 forb
        self.assertEqual(response.status_code, 200)

    # without auth
    def test_get_user(self):
        # res = User.query.filter_by(email='test2@test.com').first()
        response = self._app.get('/user/test2@test.com', headers={"token": self.bytes_to_json_token})
        self.assertEqual(response.status_code, 403)

    def test_delete_user(self):
        self.test_auth()
        response = self._app.delete('/user/test2@test.com', headers={"token": self.bytes_to_json_token})
        print("user was deleted")
        print(response.status_code)
        # self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
