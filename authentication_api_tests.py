import unittest

from src.authentication.authentication import AuthApi


class MyTestCase(unittest.TestCase):

    authObject = AuthApi("Tom", "password")

    def test_username_and_pasword(self):
        self.assertEqual("Tom", self.authObject.username)
        self.assertEqual("password", self.authObject.password)

    def test_authentication_happens_for_valid_case(self):
        status = self.authObject.connectToDatabase()
        self.assertEqual(status, True)


if __name__ == '__main__':
    unittest.main()
