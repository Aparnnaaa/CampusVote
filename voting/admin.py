from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Voter, Candidate, Election, Vote, Position
import json


@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'student_id',
                    'department', 'is_verified', 'has_voted']
    search_fields = ['name', 'student_id']
    readonly_fields = ['created_at']
    list_filter = ['department', 'is_verified']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['candidate_id', 'name', 'position',
                    'department', 'election', 'vote_count']
    search_fields = ['candidate_id', 'registration_number',
                     'name', 'position__title', 'department']
    list_filter = ['department', 'position', 'election']


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'is_active', 'show_results']
    search_fields = ['title']
    list_filter = ['is_active']
    readonly_fields = []  # Ensure 'results' is removed if not a model field

    def calculate_results(self, request, queryset):
        for election in queryset:
            results_data = {}
            # Use annotation to count related Vote objects for each candidate.
            candidates = Candidate.objects.filter(election=election).annotate(vote_total=Count('vote'))
            for candidate in candidates:
                print(f"Candidate: {candidate.candidate_id}, Votes: {candidate.vote_total}")  # Debug print
                results_data[candidate.candidate_id] = candidate.vote_total
            election.results = results_data
            election.save()
            print(f"Results saved for election: {election.title}")  # Debug print

        self.message_user(request, "Election results have been calculated and saved.")


    def show_results(self, obj):
        if obj.results:
        # Assuming 'results' is a dictionary (JSONField in model)
            formatted_results = json.dumps(obj.results, indent=4)
        # Pass formatted_results as an argument to avoid format string issues
            return format_html("<pre>{}</pre>", formatted_results)
        return "Results not yet calculated"


    show_results.short_description = "Election Results"

    actions = [calculate_results]  # Register the action


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['voter', 'candidate', 'election', 'timestamp']
    search_fields = ['voter__name', 'candidate__name']
