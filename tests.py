import unittest
import json
from transactions import app, db, routes


class BasicTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self._app = app.test_client()

    def tearDown(self):
        pass

    def test_home(self):
        response = self._app.post('/')
        self.assertEqual(200, response.status_code)

    # def test_create_user(self):
    #     firstname = "test_user1"
    #     lastname = "lastname_test1"
    #     email = "test1@test.com"
    #     password = "test_pass1"
    #
    #     user_data = json.dumps({
    #         "firstname": firstname,
    #         "lastname": lastname,
    #         "email": email,
    #         "password": password
    #     })
    #     response = self._app.post('/user', headers={"Content-Type": "application/json"}, data=user_data)
    #     print(response)
    #     self.assertEqual(500, response.status_code)


if __name__ == "__main__":
    unittest.main()
