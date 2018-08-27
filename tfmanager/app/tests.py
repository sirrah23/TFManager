from django.test import Client, TestCase
from django.contrib.auth.models import User
from app.repo import FolderRepo


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


class FolderRepoTest(TestCase):

    def setUp(self):
        self.client = Client()
        response = self.client.post(
            '/app/register/', {'username': 'nu001', 'password1': '@pass1212', 'password2': '@pass1212'})
        self.user = User.objects.all().first()

    def test_create_folder_no_parent_one(self):
        f = FolderRepo.create_folder(self.user.id, 'folder1')
        self.assertIsNotNone(f)
        self.assertEqual('id' in f, True)
        self.assertEqual('creation_time' in f, True)
        self.assertEqual(f['name'], 'folder1')
        self.assertEqual(f['deleted'], False)
        self.assertEqual(f['owner_id'], self.user.id)
        self.assertEqual(f['parent_id'], None)

    def test_create_folder_no_parent_two(self):
        f = FolderRepo.create_folder(self.user.id, 'folder2')
        self.assertIsNotNone(f)
        self.assertEqual('id' in f, True)
        self.assertEqual('creation_time' in f, True)
        self.assertEqual(f['name'], 'folder2')
        self.assertEqual(f['deleted'], False)
        self.assertEqual(f['owner_id'], self.user.id)
        self.assertEqual(f['parent_id'], None)

    def test_create_folder_with_parent(self):
        f1 = FolderRepo.create_folder(self.user.id, 'folder1')
        self.assertIsNotNone(f1)
        f2 = FolderRepo.create_folder(
            self.user.id, 'folder2', parent_id=f1['id'])
        self.assertIsNotNone(f2)

        self.assertEqual(f1['name'], 'folder1')
        self.assertEqual(f2['name'], 'folder2')
        self.assertEqual(f1['deleted'], False)
        self.assertEqual(f2['deleted'], False)
        self.assertEqual(f1['owner_id'], self.user.id)
        self.assertEqual(f2['owner_id'], self.user.id)
        self.assertEqual(f1['parent_id'], None)
        self.assertEqual(f2['parent_id'], f1['id'])
