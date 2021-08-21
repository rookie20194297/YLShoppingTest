from django.conf.urls import url
from django.views.generic.base import View

from . import views

urlpatterns = [
    #购物车管理
    url(r'^carts/$',views.CartsView.as_view(),name='info'),
    #全选的url
    url(r'carts/selection/',views.CartsSelectAllView.as_view()),
]
