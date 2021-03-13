from collections import OrderedDict
from rest_framework import serializers

from .models import Poll, Question, BaseAnswer, Option, OptionAnswer, TextAnswer, Respondent

EMPTY_VALUES = ('', None, [], ())


# Получение всех опросов
class PollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = '__all__'


# Регистрация нового респондента
class CreateRespondentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Respondent
        fields = '__all__'


# Ответ на вопрос (публикация ответа) (блок сериалайзеров)
class OptionAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionAnswer
        fields = ['response']


class TextAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextAnswer
        fields = ['response']


class CreateAnswerSerializer(serializers.ModelSerializer):
    response_options = OptionAnswerSerializer(many=True, required=False)
    response_text = TextAnswerSerializer(required=False)

    class Meta:
        model = BaseAnswer
        fields = ['question', 'respondent', 'response_options', 'response_text']

    def validate(self, attrs):

        if BaseAnswer.objects.filter(respondent=attrs['respondent'], question=attrs['question']).exists():
            raise serializers.ValidationError(
                f"Респондент '{attrs['respondent']}' уже дал ответ на вопрос '{attrs['question']}'"
            )

        if attrs['question'].q_type == 'radio':
            response_options = attrs.get('response_options', None)
            if response_options is None:
                raise serializers.ValidationError(
                    f"Необходимо передать выбранные вариант ответа в поле 'response_options' "
                )
            if len(response_options) > 1:
                raise serializers.ValidationError(
                    f"Для вопроса {attrs['question']} необходимо выбрать только один вариант"
                )
            elif len(response_options) < 1:
                raise serializers.ValidationError(
                    f"Необходимо передать выбранный вариант ответа"
                )

            options_for_this_question = Option.objects.filter(question=attrs['question'])
            if not (response_options[0]['response'] in options_for_this_question):
                raise serializers.ValidationError(
                    f"Некорректный вариант ответа '{response_options[0]['response']}' на вопрос '{attrs['question']}'. "
                    f"Данный вариант ответа относится к другому вопросу."
                )

        if attrs['question'].q_type == 'check':
            response_options = attrs.get('response_options', None)
            if response_options is None:
                raise serializers.ValidationError(
                    f"Необходимо передать выбранные вариант ответа в поле 'response_options' "
                )

            if len(response_options) < 1:
                raise serializers.ValidationError(
                    f"Необходимо передать выбранные вариант ответа"
                )
            options_for_this_question = Option.objects.filter(question=attrs['question'])
            for option in response_options:
                if not (option['response'] in options_for_this_question):
                    raise serializers.ValidationError(
                        f"Некорректный вариант ответа '{option['response']}' на вопрос '{attrs['question']}'. "
                        f"Данный вариант ответа относится к другому вопросу."
                    )

        if attrs['question'].q_type == 'text':
            response_text = attrs.get('response_text', None)
            if response_text is None:
                raise serializers.ValidationError(
                    f"Необходимо передать ответ в поле 'response_text' "
                )

        return attrs

    def create(self, validated_data):

        if validated_data['question'].q_type == 'radio':
            response_options = validated_data.pop('response_options')
            response = response_options.pop()
            answer = OptionAnswer.objects.create(
                question=validated_data['question'],
                respondent=validated_data['respondent'],
                response=response['response']
            )

        elif validated_data['question'].q_type == 'check':
            response_options = validated_data.pop('response_options')
            for response in response_options:
                OptionAnswer.objects.create(
                    question=validated_data['question'],
                    respondent=validated_data['respondent'],
                    response=response['response']
                )
            answer = BaseAnswer.objects.filter(
                question=validated_data['question'],
                respondent=validated_data['respondent']
            ).first()

        elif validated_data['question'].q_type == 'text':
            response = validated_data.pop('response_text')

            answer = TextAnswer.objects.create(
                question=validated_data['question'],
                respondent=validated_data['respondent'],
                response=response['response']
            )

        return answer


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
    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['poll', 'title', 'q_type', 'options']

    def create(self, validated_data):
        options_data = validated_data.pop('options', None)
        question = Question.objects.create(**validated_data)
        if options_data is not None:
            for option in options_data:
                Option.objects.create(question=question, **option)
        return question


# Обновление вопроса (блок сериалайзеров)
class UpdateOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Option
        fields = ['id', 'title']


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


# Получить всё вопросы для заданного опроса c вариантами ответов
class AllQuestionSerializer(serializers.ModelSerializer):
    options = UpdateOptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'poll', 'title', 'q_type', 'options']


# Получение пройденных опросов с вопросами и ответами (блок сериалайзеров)
class DetailOptionAnswerSerializer(serializers.ModelSerializer):

    response = serializers.StringRelatedField()

    class Meta:
        model = OptionAnswer
        fields = ['response']


class AnswerSerializer(serializers.ModelSerializer):

    answer_option = DetailOptionAnswerSerializer(read_only=True, required=False)
    answer_text = TextAnswerSerializer(read_only=True, required=False)

    class Meta:
        model = BaseAnswer
        fields = ['answer_option', 'answer_text']

    def to_representation(self, instance):
        fields = super().to_representation(instance)
        return OrderedDict((k, v) for k, v in fields.items()
                           if v not in EMPTY_VALUES)


class QuestionSerializer(serializers.ModelSerializer):

    answer = serializers.SerializerMethodField('get_answer')

    def get_answer(self, question):
        answer = BaseAnswer.objects.filter(
            respondent=self.context['respondent_id'],
            question=question,
        )
        answer_serializer = AnswerSerializer(instance=answer, many=True)
        return answer_serializer.data

    class Meta:
        model = Question
        fields = ['id', 'title', 'answer']


class RespondentPollSerializer(serializers.ModelSerializer):

    questions = serializers.SerializerMethodField('get_questions')
    poll = serializers.CharField(source='title')

    def get_questions(self, poll):
        questions = Question.objects.filter(question__respondent=self.context['respondent_id']).distinct()
        questions_serializer = QuestionSerializer(
            instance=questions,
            many=True,
            context={'respondent_id': self.context['respondent_id']}
        )
        return questions_serializer.data

    class Meta:
        model = Poll
        fields = ['poll', 'id', 'questions', ]
