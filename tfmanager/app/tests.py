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
        self.user = User.objects.all()[0]
        response = self.client.post(
            '/app/register/', {'username': 'nu002', 'password1': '@pass1212', 'password2': '@pass1212'})
        self.user_two = User.objects.all()[1]

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

    def test_get_user_folders(self):
        f1 = FolderRepo.create_folder(self.user.id, 'folder1')
        f2 = FolderRepo.create_folder(self.user.id, 'folder2')
        f3 = FolderRepo.create_folder(self.user.id, 'folder3')
        all_f = FolderRepo.get_all_folder_for_user(self.user.id)
        self.assertEqual(len(all_f), 3)
        self.assertIn(f1, all_f)
        self.assertIn(f2, all_f)
        self.assertIn(f3, all_f)

    def test_get_user_folders_some_parents(self):
        f1 = FolderRepo.create_folder(self.user.id, 'folder1')
        f2 = FolderRepo.create_folder(self.user.id, 'folder2', parent_id=f1['id'])
        f3 = FolderRepo.create_folder(self.user.id, 'folder3', parent_id=f2['id'])
        all_f = FolderRepo.get_all_folder_for_user(self.user.id)
        self.assertEqual(len(all_f), 3)
        self.assertIn(f1, all_f)
        self.assertIn(f2, all_f)
        self.assertIn(f3, all_f) 

    def test_get_user_folders_multiple_users(self):
        f1 = FolderRepo.create_folder(self.user.id, 'folder1')
        f2 = FolderRepo.create_folder(self.user_two.id, 'folder2')
        f3 = FolderRepo.create_folder(self.user.id, 'folder3', parent_id=f1['id'])
        all_f_one = FolderRepo.get_all_folder_for_user(self.user.id)
        all_f_two = FolderRepo.get_all_folder_for_user(self.user_two.id)
        self.assertEqual(len(all_f_one), 2)
        self.assertEqual(len(all_f_two), 1)
        self.assertIn(f1, all_f_one)
        self.assertIn(f3, all_f_one) 
        self.assertIn(f2, all_f_two)

    def test_delete_folder(self):
        f1 = FolderRepo.create_folder(self.user.id, 'folder1')
        stat = FolderRepo.delete_folder(self.user.id, f1['id'])
        self.assertTrue(stat)

    def test_delete_not_your_folder(self):
        f1 = FolderRepo.create_folder(self.user.id, 'folder1')
        stat = FolderRepo.delete_folder(self.user_two.id, f1['id'])
        self.assertFalse(stat)

    def test_delete_nonexistent_folder(self):
        stat = FolderRepo.delete_folder(self.user.id, 322)
        self.assertFalse(stat)

    def test_get_user_folders_with_parent_root(self):
        f1 = FolderRepo.create_folder(self.user.id, 'folder1')
        f2 = FolderRepo.create_folder(self.user.id, 'folder2')
        f3 = FolderRepo.create_folder(self.user_two.id, 'folder3')
        all_f_one = FolderRepo.get_all_folder_for_user_with_parent(self.user.id, None)
        all_f_two = FolderRepo.get_all_folder_for_user_with_parent(self.user_two.id, None)
        self.assertEqual(len(all_f_one), 2)
        self.assertEqual(len(all_f_two), 1)
        self.assertIn(f1, all_f_one)
        self.assertIn(f2, all_f_one)
        self.assertIn(f3, all_f_two)

    def test_get_user_folders_with_mixed_parent(self):
        f1 = FolderRepo.create_folder(self.user.id, 'folder1')
        f2 = FolderRepo.create_folder(self.user.id, 'folder2', parent_id=f1['id'])
        f3 = FolderRepo.create_folder(self.user.id, 'folder3', parent_id=f1['id'])
        all_f_no_parent = FolderRepo.get_all_folder_for_user_with_parent(self.user.id, None)
        all_f_parent = FolderRepo.get_all_folder_for_user_with_parent(self.user.id, f1['id'])
        self.assertEqual(len(all_f_no_parent), 1)
        self.assertEqual(len(all_f_parent), 2)
        self.assertIn(f1, all_f_no_parent)
        self.assertIn(f2, all_f_parent)
        self.assertIn(f3, all_f_parent)

    def test_get_user_folders_with_mixed_parent(self):
        f1 = FolderRepo.create_folder(self.user.id, 'folder1')
        f2 = FolderRepo.create_folder(self.user_two.id, 'folder2')
        f3 = FolderRepo.create_folder(self.user.id, 'folder3', parent_id=f1['id'])
        f4 = FolderRepo.create_folder(self.user_two.id, 'folder4', parent_id=f2['id'])
        all_f_one = FolderRepo.get_all_folder_for_user_with_parent(self.user.id, f1['id'])
        all_f_two = FolderRepo.get_all_folder_for_user_with_parent(self.user_two.id, f2['id'])
        self.assertEqual(len(all_f_one), 1)
        self.assertEqual(len(all_f_two), 1)
        self.assertIn(f3, all_f_one)
        self.assertIn(f4, all_f_two)
