from django.db.models import Q
from rest_framework import serializers

from .models import Poll, Question, BaseAnswer, Option


# Получение всех опросов
class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = '__all__'


# Получение пройденных опросов с вопросами и ответами
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


# Админские сериалайзеры
# Обновление опроса
class UpdatePollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = ['title', 'description', 'end_date']


# Добавление нового опроса
class AddPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = '__all__'


# Получить всё вопросы для заданного опроса (для администраторов)
class AllQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


# Добавление нового вопроса (блок сериалайзеров)
class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['title']


class AddQuestionSerializer(serializers.ModelSerializer):

    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['poll', 'title', 'q_type', 'options']

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        question = Question.objects.create(**validated_data)
        for option in options_data:
            Option.objects.create(question=question, **option)
        return question


# Обновление вопроса
class UpdateQuestionSerializer(serializers.ModelSerializer):

    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['title', 'q_type', 'poll', 'options']

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


