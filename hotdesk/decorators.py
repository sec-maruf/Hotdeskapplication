# decorators.py

from django.shortcuts import redirect
from functools import wraps

def solid_username_required(allowed_usernames):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            solid_username = request.session.get('solid_credentials', {}).get('username')
            if solid_username in allowed_usernames:
                return view_func(request, *args, **kwargs)
            else:
                # Redirect to a denied access page or login page
                return redirect('solid-login')
        return _wrapped_view
    return decorator

