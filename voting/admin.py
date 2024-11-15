from django.contrib import admin
from .models import Voter, Candidate, Election, Vote

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'student_id', 'department', 'is_verified', 'has_voted']
    search_fields = ['name', 'student_id']
    readonly_fields = ['created_at']
    list_filter = ['department', 'is_verified']

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'department', 'election', 'vote_count']
    search_fields = ['name', 'position', 'department']
    list_filter = ['position', 'department', 'election']

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'is_active']
    search_fields = ['title']
    list_filter = ['is_active']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['voter', 'candidate', 'election', 'timestamp']
    search_fields = ['voter__name', 'candidate__name']
