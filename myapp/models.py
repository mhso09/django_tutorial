from platform import release
from tkinter import CASCADE
from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Question(models.Model):
    subject = models.CharField(max_length=200) # 제목(최대글자수)
    content = models.TextField() # 내용
    create_date = models.DateTimeField(auto_now_add=True) # 작성일
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_question') # 작성자
    modify_date = models.DateTimeField(null=True, blank=True) # 수정일
    voter = models.ManyToManyField(User, related_name='voter_question') # 추천인

    # str을 써줌으로 제목을 subject로 바꿈
    def __str__(self):
        return self.subject

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author_answer')
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User, related_name='voter_answer')
