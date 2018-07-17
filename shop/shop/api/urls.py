from django.conf.urls import url
from rest_framework.authtoken import views as drf_views
from shop.api.views import User, Logout, ObtainExpiringAuthToken, AllStock, StockShareHolder, StockDetail

urlpatterns = [
    # url(r'^auth$', drf_views.obtain_auth_token, name='auth'),
    url(r'^auth$', ObtainExpiringAuthToken.as_view()),
    url(r'^logout$', Logout.as_view(), name='logout'),
    url(r'^user$', User.as_view(), name='get_user_detail'),
    url(r'^stock$', AllStock.as_view(), name='get_all_stocks'),
    url(r'^shareholder/(?P<stock_id>.+)/', StockShareHolder.as_view(), name='get_all_shareholder_id'),
    url(r'^shareholder$', StockShareHolder.as_view(), name='get_all_shareholder'),
    url(r'^stock/detail$', StockDetail.as_view(), name='get_stock_detail')
]
