from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.voter_login, name='voter_login'),
    path('dashboard/', views.voter_dashboard, name='voter_dashboard'),
    path('logout/', views.voter_logout, name='voter_logout'),
    path('elections/', views.elections_list, name='elections_list'),
    path('elections/<int:election_id>/',
         views.election_details, name='election_details'),
]
