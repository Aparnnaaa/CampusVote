from .utils import voter_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import Voter, Election, Candidate, Vote
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


def voter_login(request):

    if request.session.get("voter_id"):
        return redirect('voter_dashboard')

    if request.method == 'POST':
        student_id = request.POST['student_id']
        password = request.POST['password']
        try:
            voter = Voter.objects.get(student_id=student_id)
            if check_password(password, voter.password):
                request.session['voter_id'] = voter.voter_id
                return redirect('voter_dashboard')
            else:
                messages.error(request, 'Invalid password')
        except Voter.DoesNotExist:
            messages.error(request, 'Voter not found')
    return render(request, 'voter_login.html')


@voter_required
def voter_dashboard(request):
    voter_id = request.session.get('voter_id')
    if not voter_id:
        return redirect('voter_login')
    voter = Voter.objects.get(voter_id=voter_id)
    return render(request, 'voter_dashboard.html', {'voter': voter})


@voter_required
def voter_logout(request):
    request.session.flush()  # Clear session data
    return redirect('voter_login')


@voter_required
def elections_list(request):
    ongoing_elections = Election.objects.filter(is_active=True)
    return render(request, 'elections_list.html', {'elections': ongoing_elections})


@voter_required
def election_details(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    candidates = election.candidates.all()
    return render(request, 'election_details.html', {'election': election, 'candidates': candidates})


@login_required
def cast_vote(request, election_id):
    voter = request.user
    election = get_object_or_404(Election, pk=election_id)

    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        if voter.has_voted:
            return HttpResponse("You have already voted n this election.")

        candidate = get_object_or_404(Candidate, pk=candidate_id)
        if candidate.election.id != election.id:
            return HttpResponse("Invalid candidate for this election.")

        Vote.objects.create(
            voter=voter, candidate=candidate, election=election)
        voter.has_voted = True
        voter.save()
        return HttpResponse("Thank you for voting!")

    return render(request, 'cast_vote.html', {'election': election})
