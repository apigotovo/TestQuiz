from django.contrib import admin

from .models import Respondent, Option, Question, Poll

admin.site.register(Poll)
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Respondent)
