from datetime import datetime
from email.errors import MessageError
from django.shortcuts import render, HttpResponse, get_object_or_404, redirect, resolve_url
from django.http import HttpResponseNotAllowed
from .forms import AnswerForm, QuestionForm, CommentForm
from .models import Question, Answer, Comment
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
# Create your views here.

# def index(request):
#     return HttpResponse("hello")

def index(request):
    # 입력 파라미터
    page = request.GET.get('page','1') # 페이지
    kw = request.GET.get('kw',"")

    # 질문목록 데이터는 Question.objects.order_by 로 얻어온다.
    # order_by('-create_date')는 작성일시 역순으로 정렬하라
    # "-"기호가 붙으면 역방향 없으면 정방향 게시물은 보통 최신순이므로 역순정렬
    
    question_list = Question.objects.order_by('-create_date') # 조회
    
    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) | # 제목 검색
            Q(content__icontains=kw) | # 내용 검색
            Q(answer__content__icontains=kw) | # 답변 내용 검색
            Q(author__username__icontains=kw) | # 질문 작성자 검색
            Q(answer__author__username__icontains=kw) # 답글 작성자 검색
        ).distinct()
    # 페이징 처리
    paginator = Paginator(question_list, 10) # 페이지당 10개씩 보이기
    # 마지막 페이지
    max_index = len(paginator.page_range)
    page_obj = paginator.get_page(page)
    context = {'question_list' : page_obj, 'max_index':max_index, 'page':page, 'kw':kw}
    return render(request, 'question_list.html', context)

def detail(request, question_id):
    # pk는 Question 모델의 기본키인 id를 의미
    question =get_object_or_404(Question, pk=question_id)
    context = {'question':question}
    return render(request, 'question_detail.html', context)


@login_required(login_url='common:login')
def answer_create(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user  # author 속성에 로그인 계정 저장 - 로그인 상태이기에 request.user값을 가져옴
            answer.create_date = datetime.now()
            answer.question = question
            answer.save()
            return redirect('{}#answer_{}'.format(
                resolve_url('myapp:detail', question_id=question.id), answer.id))
    else:
        return HttpResponseNotAllowed('Only POST is possible.')
    context = {'question':question , 'form':form}
    #  detail 별칭은 question_id가 필요하므로 question.id를 인수로 전달했다.
    return render(request, 'question_detail.html', context)

@login_required(login_url='common:login')
def question_create(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user  # author 속성에 로그인 계정 저장
            question.create_date = datetime.now()
            question.save()
            return redirect('myapp:index')
    else:
        form = QuestionForm()
    context = {'form':form}
    return render(request, 'question_form.html', context)
    # question_create 함수는 위에서 작성한 QuestionForm을 사용했다. 
    # render 함수에 전달한 {'form': form}은 템플릿에서 질문 등록시 사용할 폼 엘리먼트를 생성할 때 쓰인다.

# 질문 수정
@login_required(login_url='common:login')
def question_modify(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.error(request, "수정권한이 없습니다.")
        return redirect("myapp:detail", question_id=question.id)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.modify_date = datetime.now()
            question.save()
            return redirect("myapp:detail", question_id=question.id)
    else:
        form = QuestionForm(instance=question)
    context = {"form":form}
    return render(request, 'question_form.html', context)

# 질문삭제
@login_required(login_url='common:login')
def question_delete(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.error(request, "권한이 없습니다.")
        return redirect("myapp:detail", question_id=question.id)
    question.delete()
    return redirect("myapp:index")

# 답글 수정
@login_required(login_url='common:login')
def answer_modify(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.author:
        messages.error(request, "수정권한이 없습니다.")
        return redirect('{}#answer_{}'.format(
            resolve_url("myapp:detail", question_id=answer.question.id), answer.id))
    if request.method == "POST":
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.modify = timezone.now()
            answer.save()
            return redirect('{}#answer_{}'.format(
                resolve_url("myapp:detail", question_id=answer.question.id), answer.id))
    else:
        form = AnswerForm(instance=answer)
    context = {"answer":answer, "form":form}
    return render(request, "answer_form.html", context)

# 답글 삭제
@login_required(login_url="common:login")
def answer_delete(request,answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.author:
        messages.error(request, "삭제 권한이 없습니다.")
    else:
        answer.delete()
    return redirect('{}#answer_{}'.format(
        resolve_url('myapp:detail', question_id=answer.question.id),answer.id))

# 질문 추천
@login_required(login_url="common:login")
def question_vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user == question.author:
        messages.error(request, "자신의 게시물에는 추천할 수 없습니다.")
    else:
        question.voter.add(request.user)
    return redirect("myapp:detail", question_id=question.id)

# 답글 추천
@login_required(login_url='common:login')
def answer_vote(request, answer_id):
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user == answer.author:
        messages.error(request, "자신이 작성한 글은 추천할 수 없습니다.")
    else:
        answer.voter.add(request.user)
    return redirect('{}#answer_{}'.format(
        resolve_url("myapp:detail", question_id=answer.question.id),answer.id))

# 질문에 대한 댓글
@login_required(login_url="common:login")
def question_comment(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.create_date = datetime.now()
            comment.question = question
            comment.save()
            return redirect('myapp:detail', question_id=question.id)
    else:
        form = CommentForm()
    context = {'form': form}
    return render(request, 'comment_form.html', context)

# 답글 삭제
@login_required(login_url="common:login")
def comment_question_delete(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, "삭제 권한이 없습니다.")
        return redirect("myapp:detail", question_id=comment.question.id)
    else:
        comment.delete()
    return redirect("myapp:detail", question_id=comment.question.id)
