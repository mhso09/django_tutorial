from django.contrib import admin
from .models import Question
# Register your models here.

#Question 모델에 세부기능 추가할 수 있는 클래스 생성
class QuestionAdmin(admin.ModelAdmin):
    # 제목 검색을 위해 search_fields 속성에 subject 추가
    search_fields = ['subject']

admin.site.register(Question, QuestionAdmin)
