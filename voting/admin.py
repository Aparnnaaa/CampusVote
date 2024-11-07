from django.contrib import admin
from .models import Voter, Candidate, Election, Vote

admin.site.register(Voter)
admin.site.register(Candidate)
admin.site.register(Election)
admin.site.register(Vote)
