
from django.urls import path
from myapp import views

app_name = "myapp"

urlpatterns = [
     # index
    path('', views.index, name='index'),
    path('<int:question_id>/', views.detail, name='detail'),

    #question
    path('question/create/', views.question_create, name='question_create'),
    path('question/modify/<int:question_id>', views.question_modify, name='question_modify'),
    path('question/delete/<int:question_id>',
         views.question_delete, name="question_delete"),
    path('question/vote/<int:question_id>',
         views.question_vote, name='question_vote'),
     
     #answer
    path('answer/create/<int:question_id>', views.answer_create, name='answer_create'),
    path('answer/modify/<int:answer_id>',
         views.answer_modify, name='answer_modify'),
     path('answer/delete/<int:answer_id>', views.answer_delete, name='answer_delete'),
     path('answer/vote/<int:answer_id>', views.answer_vote, name='answer_vote'),

     #comment
     path('comment/create/<int:question_id>', views.question_comment, name='question_comment'),
     path('comment/delete/<int:comment_id>',
          views.comment_question_delete, name='comment_question_delete'),
]

