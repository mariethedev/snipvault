# Generated by Django 5.0.4 on 2024-07-15 13:42

from django.db import migrations
from authentication.models import User, UserProfile


def create_user_profiles(apps,schema_editor):
    User = apps.get_model('authentication', 'User')
    UserProfile = apps.get_model('authentication', 'UserProfile')
    
    for user in User.objects.all():
        if not hasattr(user, 'userprofile'):  # Check if UserProfile exists
            UserProfile.objects.create(user=user)


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_userprofile'),
    ]

    operations = [
        migrations.RunPython(create_user_profiles),
    ]
