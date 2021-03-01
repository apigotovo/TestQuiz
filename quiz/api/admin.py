from django.contrib import admin

from .models import Respondent, Option, Question, Poll, BaseAnswer, OptionAnswer, TextAnswer

admin.site.register(Poll)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Respondent)
admin.site.register(BaseAnswer)
admin.site.register(OptionAnswer)
admin.site.register(TextAnswer)
