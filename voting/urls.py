from django.urls import path
from . import views

urlpatterns = [
    path('elections/', views.elections_list, name='elections_list'),
    path('elections/<int:election_id>/',
         views.election_details, name='election_details'),
]
