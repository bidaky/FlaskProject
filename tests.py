import unittest
import json
from transactions import app, db, routes


class BasicTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        # _app - для зручності, для того, щоб явно бачити, що це не просто app, який імпортований
        self._app = app.test_client()

    def tearDown(self):
        pass

    def test_home(self):
        response = self._app.post('/')
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
        # print(response)
        self.assertEqual(201, response.status_code)


if __name__ == "__main__":
    unittest.main()
