from . import views
from django.urls import path

app_name = 'userbase'

urlpatterns = [
    path('vendor', views.StaffSignup.as_view(),
         name='staff-sign-up'),
    path('customer', views.CustomerSignup.as_view(),
         name='customer-sign-up')
]
