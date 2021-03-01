import os
from datetime import datetime

from django.conf import settings
from django.db.models import Q
from rest_framework import serializers

from .models import Poll, Question, BaseAnswer, Option


def logger(message, mr_data):
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    path = os.path.join(settings.BASE_DIR, f'error_log/{now}_{message}.txt')
    file = open(path, 'w')
    file.write(str(mr_data))
    file.close()


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


# Обновление вопроса (блок сериалайзеров)
class UpdateOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Option
        fields = ['id', 'title']
        # optional_fields = ['id']


class UpdateQuestionSerializer(serializers.ModelSerializer):
    options = UpdateOptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['title', 'q_type', 'poll', 'options']

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)

        instance.title = validated_data.get('title')
        instance.q_type = validated_data.get('q_type')
        instance.poll = validated_data.get('poll')

        if options_data is not None:
            options_queryset = Option.objects.filter(question=instance)
            option_key = [key.get('id') for key in options_data]

            for option in options_queryset:
                if not (option.pk in option_key):
                    option.delete()

            for option in options_data:
                opt_id = option.pop('id', None)
                if opt_id is not None:
                    opt_item = options_queryset.get(pk=opt_id)
                    opt_item.title = option['title']
                    opt_item.save()
                else:
                    Option.objects.create(question=instance, **option)

        instance.save()
        return instance


# Получить всё вопросы для заданного опроса c вариантами ответа
class AllQuestionSerializer(serializers.ModelSerializer):
    options = UpdateOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'poll', 'title', 'q_type', 'options']
