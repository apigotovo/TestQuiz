from django.urls import path
from rest_framework.authtoken import views

from .views import ListActivePoll, ListRespondentPoll, AddPoll, DeletePoll, UpdatePoll, AddQuestion, ListAllPoll, \
    UpdateQuestion, DeleteQuestion, ListAllQuestions

urlpatterns = [
    # Опросы
    path('poll/add/', AddPoll.as_view(), name='addpoll'),
    path('poll/<int:pk>/update/', UpdatePoll.as_view(), name='editpoll'),
    path('poll/<int:pk>/delete/', DeletePoll.as_view(), name='deletepoll'),
    path('poll/all/list/', ListAllPoll.as_view(), name='listpoll'),
    # Вопросы
    path('question/add/', AddQuestion.as_view(), name='addquestion'),
    path('question/<int:pk>/update/', UpdateQuestion.as_view(), name='updatequestion'),
    path('question/<int:pk>/delete/', DeleteQuestion.as_view(), name='deletequestion'),
    path('question/<int:pk>/list/', ListAllQuestions.as_view(), name='listquestions'),
    # Прочие методы
    path('poll/active/list/', ListActivePoll.as_view(), name='listpoll'),
    path('poll/<int:pk>/list/<int:respondent_id>', ListRespondentPoll.as_view(), name='mylistpoll'),
    path('api-token-auth/', views.obtain_auth_token),
    ]
