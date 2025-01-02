from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vote, Candidate


@receiver(post_save, sender=Vote)
def update_vote_count(sender, instance, created, **kwargs):
    if created:
        candidate = instance.candidate
        candidate.vote_count += 1
        candidate.save()
