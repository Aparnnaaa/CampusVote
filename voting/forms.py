from django import forms
from .models import Candidate


class VoterLoginForm(forms.Form):
    student_id = forms.CharField(label='Student ID')
    password = forms.CharField(widget=forms.PasswordInput)


class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['manifesto', 'photo']
