from django.db.models import Q
from rest_framework import serializers

from .models import Poll, Question, BaseAnswer


# Админские сериалайзеры
class AddPollSerializer(serializers.ModelSerializer):

    class Meta:
        model = Poll
        fields = '__all__'


# Пользовательские сериалайзеры
class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):

    answer = serializers.StringRelatedField(many=True)

    class Meta:
        model = BaseAnswer
        fields = ['answer', ]


class QuestionSerializer(serializers.ModelSerializer):

    answer = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['title', 'answer']


class RespondentPollSerializer(serializers.ModelSerializer):

    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = ['title', 'description', 'questions']
