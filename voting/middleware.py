from django.shortcuts import render
from django.contrib import messages
from django.urls import resolve
from .models import Voter


class PreventAlreadyVotedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        applicable_routes = ['vote_form', 'cast_vote']
        current_route = resolve(request.path_info).url_name

        if current_route in applicable_routes:
            voter_id = request.session.get('voter_id')
            if voter_id:
                voter = Voter.objects.filter(pk=voter_id).first()
                if voter and voter.has_voted:
                    messages.error(request, "You have already voted.")
                    return render(request, 'already_voted.html')

        return self.get_response(request)

class ResultsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_template_response(self, request, response):
        if 'candidates' in response.context_data:
            for candidate in response.context_data['candidates']:
                if hasattr(candidate, 'vote_count'):
                    delattr(candidate, 'vote_count')
        return response