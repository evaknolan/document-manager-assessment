from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model

User = get_user_model()
from file_versions.models import FileVersion

class TestModels(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='user', password='password')
        file=SimpleUploadedFile(
            "test_file.txt",
            b"file contents"
        )
        self.file_version = FileVersion.objects.create(file_name='test_file.txt', file_path='documents/files/test_file.txt', user=self.user, version_number=1, file=file)

    def test_delete_file_version_on_user_delete(self):
        User.objects.filter(id=self.user.id).delete()
        self.assertRaises(FileVersion.DoesNotExist, FileVersion.objects.get, id=self.file_version.id)
