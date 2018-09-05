from django.test import Client, TestCase
from django.contrib.auth.models import User
from app.repo import FolderRepo, FileRepo


# TODO: Remove all login/logout posts with Client login/logout method


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
        f2 = FolderRepo.create_folder(
            self.user.id, 'folder2', parent_id=f1['id'])
        f3 = FolderRepo.create_folder(
            self.user.id, 'folder3', parent_id=f2['id'])
        all_f = FolderRepo.get_all_folder_for_user(self.user.id)
        self.assertEqual(len(all_f), 3)
        self.assertIn(f1, all_f)
        self.assertIn(f2, all_f)
        self.assertIn(f3, all_f)

    def test_get_user_folders_multiple_users(self):
        f1 = FolderRepo.create_folder(self.user.id, 'folder1')
        f2 = FolderRepo.create_folder(self.user_two.id, 'folder2')
        f3 = FolderRepo.create_folder(
            self.user.id, 'folder3', parent_id=f1['id'])
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
        all_f_one = FolderRepo.get_all_folder_for_user_with_parent(
            self.user.id, None)
        all_f_two = FolderRepo.get_all_folder_for_user_with_parent(
            self.user_two.id, None)
        self.assertEqual(len(all_f_one), 2)
        self.assertEqual(len(all_f_two), 1)
        self.assertIn(f1, all_f_one)
        self.assertIn(f2, all_f_one)
        self.assertIn(f3, all_f_two)

    def test_get_user_folders_with_mixed_parent(self):
        f1 = FolderRepo.create_folder(self.user.id, 'folder1')
        f2 = FolderRepo.create_folder(
            self.user.id, 'folder2', parent_id=f1['id'])
        f3 = FolderRepo.create_folder(
            self.user.id, 'folder3', parent_id=f1['id'])
        all_f_no_parent = FolderRepo.get_all_folder_for_user_with_parent(
            self.user.id, None)
        all_f_parent = FolderRepo.get_all_folder_for_user_with_parent(
            self.user.id, f1['id'])
        self.assertEqual(len(all_f_no_parent), 1)
        self.assertEqual(len(all_f_parent), 2)
        self.assertIn(f1, all_f_no_parent)
        self.assertIn(f2, all_f_parent)
        self.assertIn(f3, all_f_parent)

    def test_get_user_folders_with_mixed_parent(self):
        f1 = FolderRepo.create_folder(self.user.id, 'folder1')
        f2 = FolderRepo.create_folder(self.user_two.id, 'folder2')
        f3 = FolderRepo.create_folder(
            self.user.id, 'folder3', parent_id=f1['id'])
        f4 = FolderRepo.create_folder(
            self.user_two.id, 'folder4', parent_id=f2['id'])
        all_f_one = FolderRepo.get_all_folder_for_user_with_parent(
            self.user.id, f1['id'])
        all_f_two = FolderRepo.get_all_folder_for_user_with_parent(
            self.user_two.id, f2['id'])
        self.assertEqual(len(all_f_one), 1)
        self.assertEqual(len(all_f_two), 1)
        self.assertIn(f3, all_f_one)
        self.assertIn(f4, all_f_two)


class FileRepoTest(TestCase):

    def setUp(self):
        self.client = Client()
        response = self.client.post(
            '/app/register/', {'username': 'nu001', 'password1': '@pass1212', 'password2': '@pass1212'})
        self.user = User.objects.all()[0]
        response = self.client.post(
            '/app/register/', {'username': 'nu002', 'password1': '@pass1212', 'password2': '@pass1212'})
        self.user_two = User.objects.all()[1]

    def test_file_create_success(self):
        test_folder = FolderRepo.create_folder(self.user.id, 'folder1')
        self.assertIsNotNone(test_folder)
        test_file = FileRepo.create_file(
            self.user.id, test_folder['id'], 'test.txt', 'Hello, World')
        self.assertIsNotNone(test_file)

        self.assertEqual(test_file['name'], 'test.txt')
        self.assertEqual(test_file['deleted'], False)
        self.assertIn('creation_time', test_file)
        self.assertEqual(test_file['belong_id'], test_folder['id'])
        self.assertEqual(test_file['content_text'], 'Hello, World')
        self.assertEqual(test_file['version'], 0)

    def test_file_create_no_folder(self):
        nonexistent_folder_id = 322
        test_file = FileRepo.create_file(
            self.user.id, nonexistent_folder_id, 'test.txt', 'Hello, World')
        self.assertIsNone(test_file)

    def test_file_create_already_exists_in_folder(self):
        test_folder = FolderRepo.create_folder(self.user.id, 'folder1')
        self.assertIsNotNone(test_folder)
        test_file_one = FileRepo.create_file(
            self.user.id, test_folder['id'], 'test.txt', 'Hello, World')
        self.assertIsNotNone(test_file_one)
        test_file_two = FileRepo.create_file(
            self.user.id, test_folder['id'], 'test.txt', 'Hello, World')
        self.assertIsNone(test_file_two)

    def test_file_create_already_exists_different_folder(self):
        test_folder_one = FolderRepo.create_folder(self.user.id, 'folder1')
        test_folder_two = FolderRepo.create_folder(self.user.id, 'folder2')
        self.assertIsNotNone(test_folder_one)
        self.assertIsNotNone(test_folder_two)
        test_file_one = FileRepo.create_file(
            self.user.id, test_folder_one['id'], 'test.txt', 'Hello, World')
        self.assertIsNotNone(test_file_one)
        test_file_two = FileRepo.create_file(
            self.user.id, test_folder_two['id'], 'test.txt', 'Hello, World')
        self.assertIsNotNone(test_file_two)

        self.assertEqual(test_file_two['name'], 'test.txt')
        self.assertEqual(test_file_two['deleted'], False)
        self.assertIn('creation_time', test_file_two)
        self.assertEqual(test_file_two['belong_id'], test_folder_two['id'])
        self.assertEqual(test_file_two['content_text'], 'Hello, World')

    def test_file_create_different_user_folder(self):
        test_folder = FolderRepo.create_folder(self.user.id, 'folder1')
        self.assertIsNotNone(test_folder)
        test_file = FileRepo.create_file(
            self.user_two.id, test_folder['id'], 'test.txt', 'Hello, World')
        self.assertIsNone(test_file)

    def test_file_get_after_create(self):
        test_folder = FolderRepo.create_folder(self.user.id, 'folder1')
        self.assertIsNotNone(test_folder)
        test_file_create = FileRepo.create_file(
            self.user.id, test_folder['id'], 'test.txt', 'Hello, World')
        self.assertIsNotNone(test_file_create)

        # Correct user
        test_file_get_good = FileRepo.get_file(
            self.user.id, test_file_create['id'])
        # Wrong user
        test_file_get_bad = FileRepo.get_file(
            self.user_two.id, test_file_create['id'])

        self.assertDictEqual(test_file_get_good, test_file_create)
        self.assertIsNone(test_file_get_bad)

    def test_delete_file_after_create(self):
        test_folder = FolderRepo.create_folder(self.user.id, 'folder1')
        self.assertIsNotNone(test_folder)
        test_file = FileRepo.create_file(
            self.user.id, test_folder['id'], 'test.txt', 'Hello, World')
        self.assertIsNotNone(test_file)

        res = FileRepo.delete_file(self.user.id, test_file['id'])

        self.assertEqual(res, True)

    def test_file_within_folder(self):
        test_folder = FolderRepo.create_folder(self.user.id, 'folder1')
        self.assertIsNotNone(test_folder)
        test_file = FileRepo.create_file(
            self.user.id, test_folder['id'], 'test.txt', 'Hello, World')
        test_file_two = FileRepo.create_file(
            self.user.id, test_folder['id'], 'test2.txt', 'Hello, World Two')

        res = FileRepo.get_files_within_folder(self.user.id, test_folder['id'])
        self.assertEqual(len(res), 2)
        self.assertIn(test_file, res)
        self.assertIn(test_file_two, res)


class HomepageTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.client.post(
            '/app/register/', {'username': 'nu001', 'password1': '@pass1212', 'password2': '@pass1212'})
        self.client.logout()

    def test_homepage_get_not_logged_in(self):
        res = self.client.get('/app/')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Not authenticated', res.content)

    def test_homepage_is_logged_in_no_folders(self):
        self.client.login(username='nu001', password='@pass1212')
        res = self.client.get('/app/')
        self.assertEqual(res.status_code, 200)
        self.assertNotIn(b'Not authenticated', res.content)
        self.client.logout()

    def test_homepage_is_logged_in_two_folders(self):
        self.client.login(username='nu001', password='@pass1212')
        user_id = self.client.session['_auth_user_id']
        FolderRepo.create_folder(user_id, 'folder1')
        FolderRepo.create_folder(user_id, 'folder2')
        res = self.client.get('/app/')

        self.assertEqual(res.status_code, 200)
        self.assertIn(b'folder1', res.content)
        self.assertIn(b'folder2', res.content)

        self.client.logout()

    def test_homepage_is_logged_in_nested_folders_at_root(self):
        self.client.login(username='nu001', password='@pass1212')
        user_id = self.client.session['_auth_user_id']
        f1 = FolderRepo.create_folder(user_id, 'ParentFolder')
        f2 = FolderRepo.create_folder(
            user_id, 'ChildFolder', parent_id=f1['id'])
        res = self.client.get('/app/')

        self.assertEqual(res.status_code, 200)
        self.assertIn(b'ParentFolder', res.content)
        self.assertNotIn(b'ChildFolder', res.content)

        self.client.logout()


class FolderPageTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.client.post(
            '/app/register/', {'username': 'nu001', 'password1': '@pass1212', 'password2': '@pass1212'})
        self.client.logout()

    def test_folder_page_empty(self):
        self.client.login(username='nu001', password='@pass1212')
        user_id = self.client.session['_auth_user_id']
        f1 = FolderRepo.create_folder(user_id, 'ParentFolder')
        f2 = FolderRepo.create_folder(user_id, 'ChildFolder')
        res = self.client.get('/app/folder/{}/'.format(f1['id']))

        self.assertEqual(res.status_code, 200)
        self.assertIn(b'<h2>ParentFolder</h2>', res.content)
        self.assertNotIn(b'ChildFolder', res.content)

        self.client.logout()

    def test_folder_page_contains_subfolder(self):
        self.client.login(username='nu001', password='@pass1212')
        user_id = self.client.session['_auth_user_id']
        f1 = FolderRepo.create_folder(user_id, 'ParentFolder')
        f2 = FolderRepo.create_folder(
            user_id, 'ChildFolder', parent_id=f1['id'])
        res = self.client.get('/app/folder/{}/'.format(f1['id']))

        self.assertEqual(res.status_code, 200)
        self.assertIn(b'<h2>ParentFolder</h2>', res.content)
        self.assertIn(b'ChildFolder', res.content)

        self.client.logout()

    def test_folder_access_link_directly_empty(self):
        self.client.login(username='nu001', password='@pass1212')
        user_id = self.client.session['_auth_user_id']
        f1 = FolderRepo.create_folder(user_id, 'ParentFolder')
        f2 = FolderRepo.create_folder(
            user_id, 'ChildFolder', parent_id=f1['id'])
        res = self.client.get('/app/folder/{}/'.format(f2['id']))

        self.assertEqual(res.status_code, 200)
        self.assertIn(b'<h2>ChildFolder</h2>', res.content)

        self.client.logout()

    def test_folder_has_link_to_parent_folder(self):
        self.client.login(username='nu001', password='@pass1212')
        user_id = self.client.session['_auth_user_id']
        f1 = FolderRepo.create_folder(user_id, 'ParentFolder')
        f2 = FolderRepo.create_folder(
            user_id, 'ChildFolder', parent_id=f1['id'])
        res = self.client.get('/app/folder/{}/'.format(f2['id']))

        self.assertEqual(res.status_code, 200)
        self.assertIn(b'<h2>ChildFolder</h2>', res.content)
        self.assertIn(
            bytes('<a href="/app/folder/{}/">'.format(f1['id']), 'utf-8'), res.content)

        self.client.logout()

    def test_folder_has_files_in_it(self):
        self.client.login(username='nu001', password='@pass1212')
        user_id = self.client.session['_auth_user_id']
        f1 = FolderRepo.create_folder(user_id, 'ParentFolder')
        f2 = FolderRepo.create_folder(user_id, 'ChildFolder')
        tf = FileRepo.create_file(
            user_id, f2['id'], 'test.txt', 'Hello, World')
        res = self.client.get('/app/folder/{}/'.format(f2['id']))

        self.assertEqual(res.status_code, 200)
        self.assertIn(b'<h2>ChildFolder</h2>', res.content)
        self.assertIn(bytes(
            '<a href="/app/file/{}/">{}</a>'.format(tf['id'], tf['name']), 'utf-8'), res.content)
