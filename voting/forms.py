from django import forms

class VoterLoginForm(forms.Form):
    student_id = forms.CharField(label='Student ID')
    password = forms.Charfield(widget=forms.PasswordInput)