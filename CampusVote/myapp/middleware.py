from django.shortcuts import redirect
from django.contrib import messages
from .models import Voter


class PreventAlreadyVotedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        voter_id = request.session.get('voter_id')
        if voter_id:
            voter = Voter.objects.filter(pk=voter_id).first()
            if voter and voter .has_voted:
                messages.error(request, "You have already voted.")
                return redirect('elections_list')
        return self.get_response(request)
