from datetime import datetime



from django.db.models import Q
from django.http import HttpResponse

from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework.permissions import IsAdminUser

from .models import Poll, Question, BaseAnswer
from .serializers import PollSerializer, RespondentPollSerializer, AddPollSerializer, UpdatePollSerializer, \
    AddQuestionSerializer, AllQuestionSerializer, UpdateQuestionSerializer, CreateAnswerSerializer, \
    CreateRespondentSerializer



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

    def get_serializer_context(self):
        a = super().get_serializer_context()
        a['respondent_id'] = self.kwargs['pk']
        return a

    def get_queryset(self):
        return Poll.objects.filter(poll__question__respondent=self.kwargs['pk']).distinct()


class CreateAnswer(CreateAPIView):
    serializer_class = CreateAnswerSerializer
    queryset = BaseAnswer.objects.all()


class CreateRespondent(CreateAnswer):
    serializer_class = CreateRespondentSerializer


def api_doc(request):
    return HttpResponse(
        '<a href="https://documenter.getpostman.com/view/11811108/Tz5s2w3d">Документация по API для системы опросов</a>'
    )
