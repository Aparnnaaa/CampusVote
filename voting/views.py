from .utils import voter_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from collections import defaultdict
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
    from collections import defaultdict
    election = get_object_or_404(Election, pk=election_id)
    candidates = election.candidates.select_related(
        'position').order_by('position__title')

    grouped_candidates = {}
    for candidate in candidates:
        position_title = candidate.position.title
        if position_title not in grouped_candidates:
            grouped_candidates[position_title] = []
        grouped_candidates[position_title].append(candidate)

    return render(request, 'election_details.html', {
        'election': election,
        'grouped_candidates': grouped_candidates
    })


@voter_required
def vote_form(request, election_id):
    voter_id = request.session.get('voter_id')
    voter = get_object_or_404(Voter, pk=voter_id)
    election = get_object_or_404(Election, pk=election_id, is_active=True)

    voted_positions = Vote.objects.filter(
        voter=voter, election=election
    ).values_list('candidate__position', flat=True)

    candidates = Candidate.objects.filter(
        election=election
    ).exclude(position__in=voted_positions)

    if not candidates:
        # If no candidates are left to vote for, show a message
        messages.error(
            request, "You have already voted for all positions in this election.")
        return render(request, 'already_voted.html', {'election': election})

    return render(request, 'vote_form.html', {'election': election, 'candidates': candidates})


@ voter_required
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
    voter_id = request.session.get('voter_id')
    voter = get_object_or_404(Voter, pk=voter_id)
    election = get_object_or_404(Election, pk=election_id, is_active=True)

    if request.method == 'POST' and 'finalize_vote' in request.POST:
        candidate_id = request.POST.get('candidate_id')
        if not candidate_id:
            messages.error(request, "You must select a candidate to vote.")
            return redirect('vote_form', election_id=election_id)

        candidate = get_object_or_404(
            Candidate, pk=candidate_id, election=election)

        # Check if the voter has already voted for this position
        if Vote.objects.filter(
            voter=voter, election=election, candidate__position=candidate.position
        ).exists():
            messages.error(
                request,
                f"You have already voted for the position: {
                    candidate.position.title}."
            )
            return redirect('election_details', election_id=election_id)

        # Record the vote
        Vote.objects.create(
            voter=voter, candidate=candidate, election=election)
        candidate.vote_count += 1
        candidate.save()

        messages.success(
            request,
            f"Your vote for {candidate.name} as {
                candidate.position.title} has been cast!"
        )
        return redirect('election_details', election_id=election_id)

    return redirect('vote_form', election_id=election_id)
