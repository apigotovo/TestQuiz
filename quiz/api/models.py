from django.db import models


class Poll(models.Model):
    class Meta:
        verbose_name_plural = 'опросы'
        verbose_name = 'опрос'

    def __str__(self):
        return str(self.title)

    title = models.CharField(max_length=35, verbose_name='заголовок опроса')
    description = models.CharField(blank=True, null=True, max_length=140, verbose_name='описание')
    start_date = models.DateTimeField(verbose_name='дата/время старта')
    end_date = models.DateTimeField(blank=True, null=True, verbose_name='дата/время старта')


class Question(models.Model):
    class Meta:
        verbose_name_plural = 'вопросы'
        verbose_name = 'вопрос'

    def __str__(self):
        return str(self.title)

    QUESTION_TYPES = (
        ('radio', 'один вариант из предложенных'),
        ('check', 'один или несколько вариантов из предложенных'),
        ('text', 'произвольный текст'),
    )

    poll = models.ForeignKey(Poll, related_name='poll', unique=False, on_delete=models.CASCADE, verbose_name='опрос')
    title = models.CharField(max_length=140, verbose_name='вопрос')
    q_type = models.CharField(choices=QUESTION_TYPES, max_length=5, verbose_name='тип вопроса')


class Option(models.Model):
    class Meta:
        verbose_name_plural = 'варианты ответа'
        verbose_name = 'вариант ответа'

    def __str__(self):
        return str(self.title)

    question = models.ForeignKey(Question, related_name='options', unique=False, on_delete=models.CASCADE,
                                 verbose_name='вопрос')
    title = models.CharField(max_length=50, verbose_name='вариант ответа')


class Respondent(models.Model):

    def __str__(self):
        return str(self.pk)

    class Meta:
        verbose_name_plural = 'пользователи'
        verbose_name = 'пользователь'


class BaseAnswer(models.Model):

    def __str__(self):
        return 'Ответ ' + str(self.respondent) + ' на ' + str(self.question)

    class Meta:
        verbose_name_plural = 'ответы'
        verbose_name = 'ответ'

    question = models.ForeignKey(Question, related_name='question', unique=False, on_delete=models.CASCADE,
                                 verbose_name='вопрос')
    respondent = models.ForeignKey(Respondent, related_name='respondent', unique=False, on_delete=models.CASCADE,
                                   verbose_name='пользователь')


class TextAnswer(BaseAnswer):

    def __str__(self):
        return str(self.response)

    class Meta:
        verbose_name_plural = 'тексты'
        verbose_name = 'текст'

    response = models.TextField(verbose_name='ответ текстом')
    pm_link = models.OneToOneField(BaseAnswer, on_delete=models.CASCADE, parent_link=True, related_name='answer_text')


class OptionAnswer(BaseAnswer):

    def __str__(self):
        return str(self.response)

    class Meta:
        verbose_name_plural = 'выбранные опции'
        verbose_name = 'выбранная опция'

    response = models.ForeignKey(Option, related_name='response', unique=False, verbose_name='ответ из вариантов',
                                 on_delete=models.CASCADE)
    pm_link = models.OneToOneField(BaseAnswer, on_delete=models.CASCADE, parent_link=True, related_name='answer_option')
