from .utils import voter_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import Voter, Election, Candidate, Vote


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
    candidates = election.candidates.all()  # Using related_name in Candidate model

    return render(request, 'election_details.html', {'election': election, 'candidates': candidates})


@voter_required
def vote_form(request, election_id):
    election = get_object_or_404(Election, pk=election_id, is_active=True)
    candidates = Candidate.objects.filter(election=election)
    return render(request, 'vote_form.html', {'election': election, 'candidates': candidates})


@voter_required
def confirm_vote(request, election_id):
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        election = get_object_or_404(Election, pk=election_id, is_active=True)
        candidate = get_object_or_404(
            Candidate, pk=candidate_id, election=election)
        return render(request, 'confirm_vote.html', {'election': election, 'candidate': candidate})
    return redirect('vote_form', election_id=election_id)


@voter_required
def cast_vote(request, election_id):
    if request.method == 'POST' and 'finalize_vote' in request.POST:
        voter_id = request.session.get('voter_id')
        voter = get_object_or_404(Voter, pk=voter_id)
        election = get_object_or_404(Election, pk=election_id, is_active=True)

        if Vote.objects.filter(voter=voter, election=election).exists():
            messages.error(request, "You have already voted in this election.")
            return redirect('elections_list')

        candidate_id = request.POST.get('candidate_id')
        candidate = get_object_or_404(
            Candidate, pk=candidate_id, election=election)

        Vote.objects.create(
            voter=voter, candidate=candidate, election=election)
        voter.has_voted = True
        voter.save()

        messages.success(request, "Thank you for voting!")
        return redirect('elections_list')
    return redirect('vote_form', election_id=election_id)
