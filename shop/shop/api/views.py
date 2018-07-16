from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class User(APIView):
    authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        content = {
            'username': request.user.username,
            'email': request.user.email,
            'groups': [g.name for g in request.user.groups.all()],
            'is_active': request.user.is_active,
            'is_superuser': request.user.is_superuser,
            'user_permissions': [{
                'name': p.name,
                'codename': p.codename,
            } for p in request.user.user_permissions.all()],
            'last_login': request.user.last_login,
            'date_joined': request.user.date_joined,
        }
        return Response(content)


class Logout(APIView):
    # authentication_classes = (TokenAuthentication, SessionAuthentication, BasicAuthentication)
    # permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)
