from django.db import models
from django.contrib.auth.models import User


class Folder(models.Model):
    name = models.CharField(max_length=50)
    deleted = models.BooleanField(default=False)
    creation_time = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owned_folders')
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='child_folders', blank=True, null=True)


class File(models.Model):
    name = models.CharField(max_length=50)
    deleted = models.BooleanField(default=False)
    creation_time = models.DateTimeField(auto_now=True)
    belong = models.ForeignKey(
        Folder, on_delete=models.CASCADE, related_name='owned_files', blank=True, null=True)


class Content(models.Model):
    text = models.TextField()
    version = models.PositiveIntegerField()
    file = models.ForeignKey(
        File, on_delete=models.CASCADE, related_name='file_content')
