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
        # firstname = "test_user2"
        # lastname = "lastname_test2"
        # email = "test2@test.com"
        # password = "test_pass2"

        # user_data = json.dumps({
        #     "firstname": firstname,
        #     "lastname": lastname,
        #     "email": email,
        #     "password": password
        # })
        # print(user_data)

        is_user = 403 if User.query.filter_by(email='test2@test.com').first() else 201
        response = self._app.post('/user', headers={"Content-Type": "multipart/form-data"},
                                  data={"firstname": "test_user2", "lastname": "lastname_test2",
                                        "email": "test2@test.com", "password": "test_pass2"})
        # print(User.query.all())
        self.assertEqual(is_user, response.status_code)

    def test_create_user_wrong_email(self):
        response = self._app.post('/user', headers={"Content-Type": "multipart/form-data"},
                                  data={"firstname": "test_user2", "lastname": "lastname_test2",
                                        "email": "I-AM-WRONG", "password": "test_pass2"})
        print(response)
        self.assertEqual(400, response.status_code)

    def test_create_user_wrong_data(self):
        response = self._app.post('/user', headers={"Content-Type": "multipart/form-data"},
                                  data={"firstname": "", "lastname": "",
                                        "email": "validation@error.test", "password": "1234567"})
        self.assertEqual(405, response.status_code)

    def test_user_update(self):
        self.test_auth()
        response = self._app.put('/user/test2@test.com',
                                 headers={"Content-Type": "multipart/form-data", "token": self.bytes_to_json_token},
                                 data={"firstname": "updated test_user2", "lastname": "updated lastname_test2",
                                       "email": "test2@test.com", "password": "test_pass2"})
        self.assertEqual(201, response.status_code)

    def test_user_update_wrong_data(self):
        self.test_auth()
        response = self._app.put('/user/test2@test.com',
                                 headers={"Content-Type": "multipart/form-data", "token": self.bytes_to_json_token},
                                 data={"firstname": "", "lastname": "",
                                       "email": "test2@test.com", "password": "1234567"})
        self.assertEqual(405, response.status_code)

    def test_auth(self):
        self.test_create_user()
        # email = "test2@test.com"
        # password = "test_pass2"
        #
        # user_data = json.dumps({
        #     "email": email,
        #     "password": password
        # })

        response = self._app.post('/authentification', headers={"Content-Type": "multipart/form-data"},
                                  data={"email": "test2@test.com", "password": "test_pass2"})

        bytes_response = response.data.decode('utf-8').replace("'", '"')
        self.bytes_to_json_token = json.loads(bytes_response)['token']

    def test_auth_wrong_pass(self):
        response = self._app.post('/authentification', headers={"Content-Type": "multipart/form-data"},
                                  data={"email": "test2@test.com", "password": "WRONG-PASSWORD"})
        self.assertEqual(response.status_code, 403)

    def test_auth_get_user(self):
        self.test_auth()
        response = self._app.get('/user/test2@test.com', headers={"token": self.bytes_to_json_token})  # or 403 forb
        self.assertEqual(response.status_code, 200)

    def test_no_auth_get_user(self):
        response = self._app.get('/user/test2@test.com', headers={"token": self.bytes_to_json_token})
        self.assertEqual(response.status_code, 403)

    def test_delete_user(self):
        self.test_auth()
        response = self._app.delete('/user/test2@test.com', headers={"token": self.bytes_to_json_token})
        self.assertEqual(response.status_code, 200)

    def test_create_wallet(self):
        self.test_auth()
        response = self._app.post('/wallets/4', headers={"token": self.bytes_to_json_token})
        print(response.status_code)
        self.assertEqual(response.status_code, 201)

    def test_create_wallet_wrong_data(self):
        self.test_auth()
        response = self._app.post('/wallets/None', headers={"token": self.bytes_to_json_token})
        print(response.status_code)
        self.assertEqual(response.status_code, 405)

    def test_delete_wallet(self):
        wallet_to_delete = Wallet.query.filter_by(id=1).first()
        response = self._app.delete('/wallets/1')
        self.assertEqual(200 if wallet_to_delete is not None else 404, response.status_code)


if __name__ == "__main__":
    unittest.main()
