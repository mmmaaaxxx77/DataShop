from django.conf.urls import url
from rest_framework.authtoken import views as drf_views
from shop.api.views import User, Logout, ObtainExpiringAuthToken

urlpatterns = [
    #url(r'^auth$', drf_views.obtain_auth_token, name='auth'),
    url(r'^auth$', ObtainExpiringAuthToken.as_view()),
    url(r'^logout', Logout.as_view(), name='logout'),
    url(r'^user$', User.as_view(), name='get_user_detail')
]