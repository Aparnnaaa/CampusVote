from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import Voter, Election, Candidate


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


def voter_dashboard(request):
    voter_id = request.session.get('voter_id')
    if not voter_id:
        return redirect('voter_login')
    voter = Voter.objects.get(voter_id=voter_id)
    return render(request, 'voter_dashboard.html', {'voter': voter})


def voter_logout(request):
    request.session.flush()  # Clear session data
    return redirect('voter_login')


def elections_list(request):
    ongoing_elections = Election.objects.filter(is_active=True)
    return render(request, 'elections_list.html', {'elections': ongoing_elections})


def election_details(request, election_id):
    election = get_object_or_404(Election, pk=election_id)
    candidates = election.candidates.all()
    return render(request, 'election_details.html', {'election': election, 'candidates': candidates})
