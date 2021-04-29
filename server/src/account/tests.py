from test import TestCase


class UserAPITest(TestCase):
    def setup(self):
        self.url = self.get_url('UserAPI')
        self.user = self.create_user()

    def user_get_test(self):
        resp = self.get(self.url)
        return self.assert_success(resp.json())


class AuthAPITest(TestCase):
    def setup(self):
        self.login_url = self.get_url('LoginAPI')
        self.register_url = self.get_url('RegisterAPI')

    def login_test(self):
        self.user = self.create_user(test_username='abc', test_password='123', login=False)
        resp = self.post(self.login_url, data={'username': 'abc', 'password': '123'})
        return self.assert_success(resp.json())

    def register_test(self):
        resp = self.post(self.register_url, data={'username': 'abc', 'password': '123'})
        return self.assert_success(resp.json())
