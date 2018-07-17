import datetime

import pytz
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted')

        # This is required for the time comparison
        utc_now = datetime.datetime.utcnow()
        utc_now = utc_now.replace(tzinfo=pytz.utc)

        if token.created < utc_now - datetime.timedelta(hours=3):
            raise AuthenticationFailed('Token has expired')

        return token.user, token


class ObtainExpiringAuthToken(ObtainAuthToken):
    def post(self, request):
        print(request)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token, created = Token.objects.get_or_create(user=serializer.validated_data['user'])

            if not created:
                # update the created time of the token to keep it valid
                token.created = datetime.datetime.utcnow()
                token.save()

            return Response({'token': token.key})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
