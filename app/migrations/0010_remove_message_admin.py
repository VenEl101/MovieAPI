# Generated by Django 5.2 on 2025-05-16 11:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_remove_adminanswer_chat'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='admin',
        ),
    ]
