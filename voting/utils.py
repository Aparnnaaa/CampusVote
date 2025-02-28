from django.shortcuts import redirect
import secrets
import string
from django.core.mail import send_mail


def voter_required(view_func):
    def wrapper(request, *args, **kwargs):
        voter_id = request.session.get('voter_id')
        if not voter_id:
            return redirect('voter_login')
        return view_func(request, *args, **kwargs)
    return wrapper


def generate_random_password(length=12):
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

def send_credentials_email(user_type, email, user_id, password):
    subject = f"Your {user_type.capitalize()} Credentials"
    message = f"""
    Your login credentials for CampusVote:
    
    {user_type.title()} ID: {user_id}
    Password: {password}
    
    Please keep this information secure.
    """
    send_mail(
        subject,
        message.strip(),
        'admin@campusvote.com',
        [email],
        fail_silently=False,
    )