from django.db import models
from django.utils import timezone

class Voter(models.Model):
    voter_id = models.AutoField(primary_key=True)  # Automatically generated unique ID
    name = models.CharField(max_length=100)        # Student's name
    email = models.EmailField(unique=True)         # Unique email for each voter
    mobile_number = models.CharField(max_length=15, blank=True, null=True)  # Optional mobile number
    student_id = models.CharField(max_length=20, unique=True)  # Unique ID issued by the college
    password = models.CharField(max_length=100)    # Hashed password for authentication
    department = models.CharField(max_length=100)  # Department name
    is_verified = models.BooleanField(default=False)  # Verification status
    has_voted = models.BooleanField(default=False)    # Voting status
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of creation
    
    def __str__(self):
        return f"{self.name} - {self.student_id}"
    
    class Election(models.Model):
        election_id = models.AutoField(primary_key=True)
        title = models.CharField(max_length=100)
        description = models.TextField()
        start_date = models.DateTimeField()
        end_date = models.DateTimeField()
        is_active = models.BooleanField()

        def __str__(self):
            return self.title
        
        @property
        def is_ongoing(self):
            now = timezone.now()
            return self.stat_date <= now <= self.end_date
        

