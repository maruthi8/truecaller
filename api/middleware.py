import jwt
from django.conf import settings
from django.contrib.auth.middleware import get_user
from django.contrib.auth.models import AnonymousUser

from api.models import User


class JWTAuthMiddleware(object):
    def __init__(self, get_response):
        """
        One-time configuration and initialisation.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Code to be executed for each request before the view (and later
        middleware) are called.
        """
        self.process_request(request)
        response = self.get_response(request)
        return response

    def process_request(self, request):
        user = get_user(request)
        if user.is_authenticated:
            request.user = user
            return
        token = request.META.get("HTTP_AUTHORIZATION")
        user = AnonymousUser
        if token:
            try:
                user_jwt = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user = User.objects.get(id=user_jwt["user_id"])
            except Exception:
                user = AnonymousUser
        request.user = user
