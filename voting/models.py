from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password


class Voter(models.Model):
    voter_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    student_id = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)
    has_voted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Candidate(models.Model):
    candidate_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    manifesto = models.TextField()
    department = models.CharField(max_length=100)
    position = models.ForeignKey(
        'Position', on_delete=models.CASCADE, related_name='candidates')
    photo = models.ImageField(
        upload_to='candidate_photos/', blank=True, null=True)
    election = models.ForeignKey(
        'election', on_delete=models.CASCADE, related_name='candidates')
    vote_count = models.IntegerField(default=0)

    password = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.position.title}"


class Election(models.Model):
    election_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField()
    results_calculated = models.BooleanField(default=False)
    results = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date


class Vote(models.Model):
    vote_id = models.AutoField(primary_key=True)
    voter = models.ForeignKey(Voter, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        # UniqueConstraint on voter and candidate (to handle one vote per position programmatically)
        constraints = [
            models.UniqueConstraint(
                fields=['voter', 'candidate'], name='unique_vote_per_candidate')
        ]

    def __str__(self):
        return f"Vote by {self.voter.name} for {self.candidate.name} in {self.candidate.position.title}"


class Position(models.Model):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title
