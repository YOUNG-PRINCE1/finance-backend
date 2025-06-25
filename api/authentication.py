# authentication.py

from firebase_admin import auth
from rest_framework.response import Response
from rest_framework import status
from functools import wraps


def firebase_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_parts = auth_header.split('Bearer ')
        if len(token_parts) != 2:
            return Response({'error': 'Authorization token missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            decoded_token = auth.verify_id_token(token_parts[1])
            request.firebase_uid = decoded_token['uid']
            return view_func(request, *args, **kwargs)
        except Exception:
            return Response({'error': 'Invalid Firebase token'}, status=status.HTTP_401_UNAUTHORIZED)

    return _wrapped_view
