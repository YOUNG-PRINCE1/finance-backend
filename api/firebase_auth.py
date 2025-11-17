import firebase_admin
from firebase_admin import auth, credentials
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
import json
import os

# 🔐 Lazy Firebase initialization
firebase_app = None

def get_firebase_app():
    global firebase_app
    if not firebase_app:
        firebase_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")
        if not firebase_json:
            raise ValueError(
                "🔥 FIREBASE_SERVICE_ACCOUNT_KEY environment variable is missing! "
                "Add it inside Render → Environment Variables."
            )
        cred = credentials.Certificate(json.loads(firebase_json))
        firebase_app = firebase_admin.initialize_app(cred)
    return firebase_app


# 🌐 Firebase Authentication class for DRF
class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.split("Bearer ")[-1]
        try:
            app = get_firebase_app()  # Lazy init
            decoded_token = auth.verify_id_token(token, app)
        except Exception:
            raise AuthenticationFailed("Invalid Firebase token")

        uid = decoded_token["uid"]
        email = decoded_token.get("email", "")

        # Get or create Django user
        user, created = User.objects.get_or_create(
            username=uid, defaults={"email": email}
        )
        return (user, None)


# 🔐 Decorator for function-based views
def firebase_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response(
                {"detail": "Authorization header missing"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = auth_header.split("Bearer ")[-1]

        try:
            app = get_firebase_app()  # Lazy init
            decoded_token = auth.verify_id_token(token, app)
            request.firebase_uid = decoded_token["uid"]
        except Exception:
            return Response(
                {"detail": "Invalid authentication token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return view_func(request, *args, **kwargs)

    return wrapper
