# Generated by Django 2.1 on 2018-09-25 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='creation_time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]