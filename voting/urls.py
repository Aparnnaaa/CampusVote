from django.urls import path
from . import views

urlpatterns = [
    # Home URL
    path('', views.home, name='home'),
    path('rules/', views.rules, name='rules'),
    # path('test-email/', views.test_email, name='test_email'),

    # Voter URLs
    path('voter/', views.voter_redirect, name='voter_redirect'),
    path('voter/login/', views.voter_login, name='voter_login'),
    path('voter/dashboard/', views.voter_dashboard, name='voter_dashboard'),
    path('voter/logout/', views.voter_logout, name='voter_logout'),

    # Election URLs
    path('voter/dashboard/elections/', views.elections_list, name='elections_list'),
    path('voter/dashboard/elections/<int:election_id>/', views.election_details, name='election_details'),
    path('voter/election/<int:election_id>/vote/<int:position_id>/', views.vote_form, name='vote_form'),
    path('voter/elections/<int:election_id>/confirm/', views.confirm_vote, name='confirm_vote'),
    path('voter/elections/<int:election_id>/cast_vote/', views.cast_vote, name='cast_vote'),
    path('voter/election/<int:election_id>/monitor/', views.election_monitoring, name='election_monitoring'),
    path('voter/admin/election/<int:election_id>/progress/', views.admin_election_progress, name='admin_election_progress'),
    path('voter/election/<int:election_id>/results/', views.election_results, name='election_results'),
    path('voter/election/<int:election_id>/update-status/', views.update_election_status, name='update_election_status'),

    # Candidate URLs
    path('candidate/login/', views.candidate_login, name='candidate_login'),
    path('candidate/logout/', views.candidate_logout, name='candidate_logout'),
    path('candidate/dashboard/', views.candidate_dashboard, name='candidate_dashboard'),
]