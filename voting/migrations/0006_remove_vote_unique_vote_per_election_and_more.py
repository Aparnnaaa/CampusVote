# Generated by Django 5.1.3 on 2025-01-01 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0005_position_alter_candidate_position'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='vote',
            name='unique_vote_per_election',
        ),
        migrations.AddConstraint(
            model_name='vote',
            constraint=models.UniqueConstraint(fields=('voter', 'candidate'), name='unique_vote_per_candidate'),
        ),
    ]
