from django.db import models

class FileVersion(models.Model):
    file_name = models.fields.CharField(max_length=512)
    version_number = models.fields.IntegerField(editable=False, blank=True)
    file_path = models.fields.CharField(max_length=512)
    file = models.FileField()
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.file_path

    class Meta:
        unique_together = ('file_path', 'version_number', 'user')
