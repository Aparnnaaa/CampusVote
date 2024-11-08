from django.db import models
from django.utils import timezone

class Candidate(models.Model):
    candidate_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    manifesto = models.TextField()
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    photo = models.ImageField(upload_to='candidate_photos/', blank=True, null=True)
    vote_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} - {self.position}"

