# Generated by Django 5.0.4 on 2024-07-24 15:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snippets', '0007_sharedsnippet_shared_at_alter_sharedsnippet_snippet'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('snippet', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='snippets.snippet')),
            ],
        ),
    ]