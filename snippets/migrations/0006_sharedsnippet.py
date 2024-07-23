# Generated by Django 5.0.4 on 2024-07-21 14:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('snippets', '0005_snippet_description_snippet_tags'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SharedSnippet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('can_edit', models.BooleanField(default='False')),
                ('shared_with', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('snippet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='snippets.snippet')),
            ],
            options={
                'unique_together': {('snippet', 'shared_with')},
            },
        ),
    ]