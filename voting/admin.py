from django.contrib import admin
from .models import Voter, Candidate, Election, Vote

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'student_id', 'department', 'is_verified', 'has_voted']
    search_fields = ['name', 'student_id']
    readonly_fields = ['created_at']
    exclude = ['password']
    list_filter = ['department', 'is_verified']

admin.site.register(Candidate)
admin.site.register(Election)
admin.site.register(Vote)
