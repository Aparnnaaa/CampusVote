# Generated by Django 5.1.1 on 2025-02-13 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0009_alter_candidate_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='registration_number',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
