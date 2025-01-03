from django.contrib.admin.views.decorators import staff_member_required
from .utils import voter_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.db.models import F
from .models import Position, Voter, Election, Candidate, Vote


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
def vote_form(request, election_id, position_id):
    voter_id = request.session.get('voter_id')
    voter = get_object_or_404(Voter, pk=voter_id)
    election = get_object_or_404(Election, pk=election_id, is_active=True)
    position = get_object_or_404(Position, pk=position_id)

    # Check if the voter has already voted for this position
    if Vote.objects.filter(
        voter=voter, election=election, candidate__position=position
    ).exists():
        return render(request, 'already_voted.html', {
            'election': election,
            'position': position,
        })

    # Filter candidates for the given position
    candidates = Candidate.objects.filter(
        election=election, position=position
    )

    if not candidates:
        messages.error(
            request, "No candidates are available for this position."
        )
        return redirect('election_details', election_id=election_id)

    return render(request, 'vote_form.html', {
        'election': election,
        'position': position,
        'candidates': candidates,
    })


@ voter_required
def confirm_vote(request, election_id):
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        election = get_object_or_404(Election, pk=election_id, is_active=True)
        candidate = get_object_or_404(
            Candidate, pk=candidate_id, election=election)
        return render(request, 'confirm_vote.html', {'election': election, 'candidate': candidate, 'position': candidate.position})
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

        # Retrieve the candidate and check election association
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

        # Record the vote and update the candidate's vote count
        Vote.objects.create(
            voter=voter, candidate=candidate, election=election)
        candidate.vote_count = F('vote_count') + 1  # Safe atomic increment
        candidate.save()

        messages.success(
            request,
            f"Your vote for {candidate.name} as {
                candidate.position.title} has been cast!"
        )
        return redirect('election_details', election_id=election_id)

    # Redirect to vote form if the request is not a POST or missing parameters
    return redirect('vote_form', election_id=election_id)


def election_monitoring(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    total_voters = Voter.objects.filter(is_verified=True).count()
    votes_cast = Vote.objects.filter(election=election).count()
    turnout_percentage = (votes_cast / total_voters) * \
        100 if total_voters > 0 else 0

    return render(request, 'election_monitoring.html', {
        'election': election,
        'votes_cast': votes_cast,
        'total_voters': total_voters,
        'turnout_percentage': turnout_percentage
    })


@staff_member_required
def admin_election_progress(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    candidates = election.candidates.all().order_by('-vote_count')  # Sort by votes
    total_votes = Vote.objects.filter(election=election).count()

    return render(request, 'admin_election_progress.html', {
        'election': election,
        'candidates': candidates,
        'total_votes': total_votes
    })
