from django.test import Client, TestCase
from django.contrib.auth.models import User


class RegistrationTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_register(self):
        response = self.client.post(
            '/app/register/', {'username': 'nu001', 'password1': '@pass1212', 'password2': '@pass1212'})
        users = User.objects.all()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].username, 'nu001')


class LoginTest(TestCase):

    def setUp(self):
        self.client = Client()
        response = self.client.post(
            '/app/register/', {'username': 'nu001', 'password1': '@pass1212', 'password2': '@pass1212'})

    def test_login_success(self):
        response = self.client.post(
            '/app/login/', {'username': 'nu001', 'password': '@pass1212'})
        # Redirect to main page of the app
        self.assertEqual(response.status_code, 302)

    def test_login_fail(self):
        response = self.client.post(
            '/app/login/', {'username': 'baduser', 'password': 'badpass'})
        # No redirect to main page of the app
        self.assertEqual(response.status_code, 200)
