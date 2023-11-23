import base64
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from file_versions.models import FileVersion
from file_versions.api.serializers import FileVersionSerializer

User = get_user_model()

class TestViews(TestCase):

    def setUp(self):
        user_name = 'user'
        password = 'password'
        self.user = User.objects.create_user(email=user_name, password=password)
        self.auth_client = Client()
        self.auth_client.login(email=user_name, password=password)
        credentials = base64.b64encode(b'user:password')
        self.auth_client.defaults['HTTP_AUTHORIZATION'] = 'Basic ' + credentials.decode("ascii")

        self.file=SimpleUploadedFile(
            "test_file.txt",
            b"file contents"
        )
        self.file_version_object = FileVersion.objects.create(file_name='test_file.txt', file_path='documents/files/test_file.txt', user=self.user, version_number=1, file=self.file)

        def tearDown(self):
            FileVersion.objects.all().delete()
            User.objects.all().delete()

    def test_list_file_versions(self):
        expected_file = FileVersionSerializer(self.file_version_object).data
        response = self.auth_client.get(reverse('api:file_versions-list'))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data[0], expected_file)

    def test_list_file_versions_no_auth(self):
        self.auth_client.logout()
        self.auth_client.defaults = {}
        response = self.auth_client.get(reverse('api:file_versions-list'))
        self.assertEquals(response.status_code, 401)

    def test_post_file_versions(self):
        new_file=SimpleUploadedFile(
            "new_file.txt",
            b"file contents"
        )
        request_data = {
            'file_name':'new_file.txt',
            'file_path':'new/path/new_file.txt',
            'user': self.user.id,
            'file':new_file
            }
        response = self.auth_client.post(reverse('api:file_versions-list'), request_data)
        file=FileVersion.objects.get(file_path='new/path/new_file.txt', version_number=1, user=self.user.id)
        file_data = FileVersionSerializer(file).data
        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data, file_data)

    def test_post_file_versions_no_auth(self):
        self.auth_client.logout()
        self.auth_client.defaults = {}
        new_file=SimpleUploadedFile(
            "new_file.txt",
            b"file contents"
        )
        request_data = {
            'file_name':'new_file.txt',
            'file_path':'new/path/new_file.txt',
            'user': self.user.id,
            'file':new_file
        }
        response = self.auth_client.post(reverse('api:file_versions-list'), request_data)
        self.assertEquals(response.status_code, 401)

    def test_post_file_versions_new_version_of_existing_file(self):
        new_file_version=SimpleUploadedFile(
            "test_file.txt",
            b"updated file contents"
        )
        request_data = {
            'file_name':'test_file.txt',
            'file_path':'documents/files/test_file.txt',
            'user': self.user.id,
            'file': new_file_version
        }
        response = self.auth_client.post(reverse('api:file_versions-list'), request_data)
        self.assertEquals(response.status_code, 201)
        self.assertEquals(response.data.get('version_number'), 2)

    def test_get_file(self):
        response = self.auth_client.get('/api/file_versions/documents/files/test_file.txt')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, 'file contents')

    def test_get_file_version(self):
        new_file_version=SimpleUploadedFile(
            "test_file.txt",
            b"updated file contents"
        )
        FileVersion.objects.create(file_name='test_file.txt', file_path='documents/files/test_file.txt', user=self.user, version_number=2, file=new_file_version)
        response = self.auth_client.get('/api/file_versions/documents/files/test_file.txt?version=2')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.data, 'updated file contents')

    def test_get_file_non_existant(self):
        response = self.auth_client.get('/api/file_versions/fake/path/test_file.txt')
        self.assertEquals(response.status_code, 404)

    def test_get_file_no_auth(self):
        self.auth_client.logout()
        self.auth_client.defaults = {}
        response = self.auth_client.get('/api/file_versions/documents/files/test_file.txt')
        self.assertEquals(response.status_code, 401)
