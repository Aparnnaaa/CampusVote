from django.contrib import admin
from django.utils.html import format_html
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
    list_display = ['candidate_id','name', 'position', 'department', 'election', 'vote_count']
    search_fields = ['candidate_id','registration -number','name', 'position_title', 'department']
    list_filter = ['department','position',  'election']

admin.site.register(Candidate, CandidateAdmin)



from django.contrib import admin
from django.utils.html import format_html
from .models import Election, Candidate
import json

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date', 'is_active', 'show_results']
    search_fields = ['title']
    list_filter = ['is_active']
    readonly_fields = ('results',)

    def calculate_results(self, request, queryset):
        for election in queryset:
            results_data = {}
            candidates = Candidate.objects.filter(election=election)

            for candidate in candidates:
                results_data[candidate.name] = candidate.vote_count
            election.results = results_data

            election.results = results_data
            election.save()

        self.message_user(request, "Election results have been calculated and saved.")

    calculate_results.short_description = "Calculate and Save Election Results"

    def show_results(self, obj):
        if obj.results:
            return json.dumps(obj.results, indent=4)
        return "Results not yet calculated"

    show_results.short_description = "Election Results"

    actions = [calculate_results]  # Register the action



@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['voter', 'candidate', 'election', 'timestamp']
    search_fields = ['voter__name', 'candidate__name']
