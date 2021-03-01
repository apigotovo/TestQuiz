from datetime import datetime

from django.conf import settings
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import redirect
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveDestroyAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.mixins import DestroyModelMixin
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Poll, Option, Question
from .serializers import PollSerializer, RespondentPollSerializer, AddPollSerializer, UpdatePollSerializer, \
    AddQuestionSerializer, AllQuestionSerializer, UpdateQuestionSerializer


# Методы для администраторов

# Обработка опросов
class AddPoll(CreateAPIView):
    serializer_class = AddPollSerializer
    permission_classes = [IsAdminUser]


class UpdatePoll(UpdateAPIView):
    serializer_class = UpdatePollSerializer
    permission_classes = [IsAdminUser]
    queryset = Poll.objects.all()


class DeletePoll(DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Poll.objects.all()


class ListAllPoll(ListAPIView):
    serializer_class = PollSerializer
    permission_classes = [IsAdminUser]
    queryset = Poll.objects.all()


# Обработка вопросов и вариантов ответа
class AddQuestion(CreateAPIView):
    serializer_class = AddQuestionSerializer
    permission_classes = [IsAdminUser]


class DeleteQuestion(DestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Question.objects.all()


class UpdateQuestion(UpdateAPIView):
    serializer_class = UpdateQuestionSerializer
    permission_classes = [IsAdminUser]
    queryset = Question.objects.all()


class ListAllQuestions(ListAPIView):
    serializer_class = AllQuestionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Question.objects.filter(poll=self.kwargs['pk'])


# Пользовательские методы
class ListActivePoll(ListAPIView):
    serializer_class = PollSerializer

    def get_queryset(self):
        now = datetime.now()
        return Poll.objects.filter(Q(start_date__date__lte=now) & (Q(end_date__date__gte=now)|Q(end_date__isnull=True)))


class ListRespondentPoll(ListAPIView):
    serializer_class = RespondentPollSerializer

    def get(self, request, *args, **kwargs):
        return Poll.objects.filter(question__baseanswer__respondent=self.kwargs['respondent_id'])
