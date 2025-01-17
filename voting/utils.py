from django.shortcuts import redirect


def voter_required(view_func):
    def wrapper(request, *args, **kwargs):
        voter_id = request.session.get('voter_id')
        if not voter_id:
            return redirect('voter_login')
        return view_func(request, *args, **kwargs)
    return wrapper

def candidate_required(view_func):
    def wrapper(request, *args, **kwargs):
        candidate_id = request.session.get('candidate_id')
        if not candidate_id:
            return redirect('candidate_login')
        return view_func(request, *args, **kwargs)
    return wrapper
