from django.db import models

def get_upload_path(instance, filename):
    # todo add path validation here
    return instance.url

class FileVersion(models.Model):
    file_name = models.fields.CharField(max_length=512)
    version_number = models.fields.IntegerField(editable=False, blank=True)
    file_path = models.fields.CharField(max_length=512)
    file = models.FileField()
    # file = models.FileField(upload_to=get_upload_path)
    # user = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('file_path', 'version_number')
