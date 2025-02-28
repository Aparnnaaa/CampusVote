from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Count
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required

from .models import Election, Candidate, Position, Voter, Vote
from .forms import CandidateProfileForm
from .utils import voter_required

# General Views


def home(request):
    return render(request, "home.html")


def voter_redirect(request):
    """
    Redirect to login if the user is not authenticated,
    otherwise redirect to the voter dashboard.
    """
    if request.user.is_authenticated:
        return redirect('voter_dashboard')
    return redirect('voter_login')

# Voter Views


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

# Election Views


@voter_required
def elections_list(request):
    all_elections = Election.objects.all().order_by('-start_date')
    return render(request, 'elections_list.html', {'elections': all_elections})


@voter_required
def election_details(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    candidates = election.candidates.select_related(
        'position').order_by('position__title')

    # Group candidates by position
    grouped_candidates = {}
    for candidate in candidates:
        position_title = candidate.position.title
        grouped_candidates.setdefault(position_title, []).append(candidate)

    return render(request, 'election_details.html', {
        'election': election,
        'grouped_candidates': grouped_candidates
    })


@require_POST
def update_election_status(request, election_id):
    try:
        election = Election.objects.get(election_id=election_id)
        now = timezone.now()
        if now >= election.end_date:
            election.is_active = False
            election.save()
            return JsonResponse({'status': 'success', 'message': 'Election status updated.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Election is still ongoing.'}, status=400)
    except Election.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Election not found.'}, status=404)


@voter_required
def vote_form(request, election_id, position_id):
    voter_id = request.session.get('voter_id')
    voter = get_object_or_404(Voter, pk=voter_id)
    election = get_object_or_404(Election, pk=election_id, is_active=True)
    position = get_object_or_404(Position, pk=position_id)

    # Check if the voter has already voted for this position
    if Vote.objects.filter(voter=voter, election=election, candidate__position=position).exists():
        return render(request, 'already_voted.html', {
            'election': election,
            'position': position,
        })

    # Filter candidates for the given position
    candidates = Candidate.objects.filter(election=election, position=position)
    if not candidates:
        messages.error(
            request, "No candidates are available for this position.")
        return redirect('election_details', election_id=election_id)

    return render(request, 'vote_form.html', {
        'election': election,
        'position': position,
        'candidates': candidates,
    })


@voter_required
def confirm_vote(request, election_id):
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        election = get_object_or_404(Election, pk=election_id, is_active=True)
        candidate = get_object_or_404(
            Candidate, pk=candidate_id, election=election)
        return render(request, 'confirm_vote.html', {
            'election': election,
            'candidate': candidate,
            'position': candidate.position
        })
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

        if Vote.objects.filter(voter=voter, election=election, candidate__position=candidate.position).exists():
            messages.error(
                request, f"You have already voted for the position: {candidate.position.title}.")
            return redirect('election_details', election_id=election_id)

        Vote.objects.create(
            voter=voter, candidate=candidate, election=election)

        messages.success(
            request, f"Your vote for {candidate.name} as {candidate.position.title} has been cast!")
        return render(request, 'vote_success.html', {
            'election': election,
            'position': candidate.position,
        })

    return redirect('vote_form', election_id=election_id)
# Candidate Views


def candidate_login(request):
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        password = request.POST.get('password')

        try:
            candidate = Candidate.objects.get(candidate_id=candidate_id)
            if check_password(password, candidate.password):
                request.session['candidate_id'] = candidate.candidate_id
                return redirect('candidate_dashboard')
            else:
                messages.error(request, "Invalid password.")
        except Candidate.DoesNotExist:
            messages.error(request, "Invalid candidate ID.")

    return render(request, 'candidate_login.html')


def candidate_logout(request):
    logout(request)  # Clear session and logout
    return redirect('candidate_login')


def candidate_dashboard(request):
    candidate_id = request.session.get('candidate_id')
    if not candidate_id:
        return redirect('candidate_login')

    try:
        candidate = Candidate.objects.get(candidate_id=candidate_id)
        print(candidate.photo)
    except ObjectDoesNotExist:
        messages.error(request, "Candidate not found")
        return redirect('candidate_login')

    if request.method == 'POST':
        form = CandidateProfileForm(
            request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('candidate_dashboard')
    else:
        form = CandidateProfileForm(instance=candidate)
    return render(request, 'candidate_dashboard.html', {'candidate': candidate, 'form': form})

# Monitoring and Admin Views


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


def election_results(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    
    if not election.results_calculated or not election.results:
        return render(request, 'results_pending.html', {'election': election})

    # Group candidates by position and identify winners
    positions = []
    position_qs = Position.objects.filter(candidates__election=election).distinct()
    
    for position in position_qs:
        candidates = []
        max_votes = 0
        
        # Get all candidates for this position
        position_candidates = Candidate.objects.filter(
            election=election, 
            position=position
        )
        
        # Annotate with results from JSON
        for candidate in position_candidates:
            candidate_data = election.results.get(str(candidate.candidate_id), {})
            votes = candidate_data.get('votes', 0)
            
            # Track max votes for winner determination
            if votes > max_votes:
                max_votes = votes
                
            candidates.append({
                'name': candidate.name,
                'votes': votes,
                'is_winner': False,
                'photo': candidate.photo.url if candidate.photo else None,
                'manifesto': candidate.manifesto
            })
        
        # Sort candidates and mark winners
        candidates.sort(key=lambda x: x['votes'], reverse=True)
        for candidate in candidates:
            if candidate['votes'] == max_votes and max_votes > 0:
                candidate['is_winner'] = True
        
        positions.append({
            'title': position.title,
            'candidates': candidates
        })
    
    return render(request, 'election_results.html', {
        'election': election,
        'positions': positions
    })