from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.voter_login, name='voter_login'),
    path('dashboard/', views.voter_dashboard, name='voter_dashboard'),
    path('logout/', views.voter_logout, name='voter_logout'),
    path('dashboard/elections/', views.elections_list, name='elections_list'),
    path('dashboard/elections/<int:election_id>/',
         views.election_details, name='election_details'),
    path('elections/<int:election_id>/vote/<str:position>/',
         views.vote_form, name='vote_form'),
    path('elections/<int:election_id>/confirm/',
         views.confirm_vote, name='confirm_vote'),
    path('elections/<int:election_id>/cast_vote/',
         views.cast_vote, name='cast_vote'),
    path('election/<int:election_id>/monitor/',
         views.election_monitoring, name='election_monitoring'),
    path('admin/election/<int:election_id>/progress/',
         views.admin_election_progress, name='admin_election_progress'),
]
