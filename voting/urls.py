from django.urls import path
from . import views

urlpatterns = [
    path('voter/login/', views.voter_login, name='voter_login'),
    path('voter/dashboard/', views.voter_dashboard, name='voter_dashboard'),
]
