from django.urls import path
from rest_framework.authtoken import views

from .views import ListPoll, ListRespondentPoll, AddPoll, DeletePoll, EditPoll

urlpatterns = [
    path('poll/add/', AddPoll.as_view(), name='addpoll'),
    path('poll/<int:pk>/update/', EditPoll.as_view(), name='editpoll'),
    path('poll/<int:pk>/delete/', DeletePoll.as_view(), name='deletepoll'),
    path('poll/active/list/', ListPoll.as_view(), name='listpoll'),
    path('mylistpoll/<int:respondent_id>', ListRespondentPoll.as_view(), name='mylistpoll'),
    path('api-token-auth/', views.obtain_auth_token),
    ]
