from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Voter, Candidate, Election, Vote, Position
import json
from django.contrib.auth.hashers import make_password
from .utils import generate_random_password, send_credentials_email

@admin.register(Voter)
class VoterAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'name', 'email', 'department']
    actions = ['send_credentials']

    def save_model(self, request, obj, form, change):
        if not change:  # Only for new creations
            plain_password = form.cleaned_data.get('password')
            obj.password = make_password(plain_password)  # Hash the password
            super().save_model(request, obj, form, change)
            send_credentials_email('voter', obj.email, obj.student_id, plain_password)
        else:
            super().save_model(request, obj, form, change)

    @admin.action(description='Send credentials to selected voters')
    def send_credentials(self, request, queryset):
        for voter in queryset:
            plain_password = generate_random_password()
            voter.password = make_password(plain_password)  # Hash the password
            voter.save()
            send_credentials_email('voter', voter.email, voter.student_id, plain_password)


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['candidate_id', 'name', 'position', 'election']
    actions = ['send_credentials']

    def save_model(self, request, obj, form, change):
        if not change:
            plain_password = form.cleaned_data.get('password')
            obj.password = make_password(plain_password)  # Hash the password
            super().save_model(request, obj, form, change)
            send_credentials_email('candidate', obj.email, obj.candidate_id, plain_password)
        else:
            super().save_model(request, obj, form, change)

    @admin.action(description='Send credentials to selected candidates')
    def send_credentials(self, request, queryset):
        for candidate in queryset:
            plain_password = generate_random_password()
            candidate.password = make_password(plain_password)  # Hash the password
            candidate.save()
            send_credentials_email('candidate', candidate.email, candidate.candidate_id, plain_password)



@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date',
                    'end_date', 'is_active', 'show_results']
    search_fields = ['title']
    list_filter = ['is_active']
    readonly_fields = []  # Ensure 'results' is removed if not a model field

    def calculate_results(self, request, queryset):
        for election in queryset:
            results_data = {}
            candidates = Candidate.objects.filter(election=election).annotate(
                vote_total=Count('vote')
            )
        
            for candidate in candidates:
                results_data[str(candidate.candidate_id)] = {
                    'name': candidate.name,
                    'votes': candidate.vote_total
                }
        
            election.is_active = False
            election.results = results_data
            election.results_calculated = True 
            election.save()
    
        self.message_user(request, "Results calculated and published!")

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
