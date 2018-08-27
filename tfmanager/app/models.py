from django.db import models
from django.contrib.auth.models import User


class Folder(models.Model):
    name = models.CharField(max_length=50)
    deleted = models.BooleanField(default=False)
    creation_time = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owner')
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='parent_folder', blank=True, null=True)


class File(models.Model):
    name = models.CharField(max_length=50)
    deleted = models.BooleanField(default=False)
    creation_time = models.DateTimeField(auto_now=True)
    belong = models.ForeignKey(
        Folder, on_delete=models.CASCADE, related_name='belong_folder', blank=True, null=True)
