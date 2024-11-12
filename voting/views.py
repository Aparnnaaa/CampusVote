from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from .models import Voter

def voter_login(request)
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
    return rende(request, 'voter_login.html')

def home(request):
    return render(request, 'voting/home.html')
