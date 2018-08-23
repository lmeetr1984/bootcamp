# coding=utf-8
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from bootcamp.questions.models import Question, Answer
from bootcamp.questions.forms import QuestionForm, AnswerForm
from bootcamp.activities.models import Activity
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from bootcamp.decorators import ajax_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
def _questions(request, questions, active):
    # 所有问题查询结果，最终要到这里来处理一下分页

    # 分页
    paginator = Paginator(questions, 10)
    page = request.GET.get('page')
    try:
        questions = paginator.page(page)
    except PageNotAnInteger:
        questions = paginator.page(1)
    except EmptyPage:
        questions = paginator.page(paginator.num_pages)
    return render(request, 'questions/questions.html', {
        'questions': questions,
        'active': active
    })


@login_required
def questions(request):
    # 主页显示所有没有被回答的问题
    return unanswered(request)


@login_required
def answered(request):
    questions = Question.get_answered()
    return _questions(request, questions, 'answered')


@login_required
def unanswered(request):
    questions = Question.get_unanswered()
    return _questions(request, questions, 'unanswered')


@login_required
def all(request):
    questions = Question.objects.all()
    return _questions(request, questions, 'all')


@login_required
def ask(request):
    # 提问按钮
    if request.method == 'POST':
        # post是提交问题
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = Question()
            question.user = request.user
            question.title = form.cleaned_data.get('title')
            question.description = form.cleaned_data.get('description')
            question.save()
            tags = form.cleaned_data.get('tags')
            question.create_tags(tags)

            # 重定向到提问页面
            return redirect('/questions/')

        else:
            return render(request, 'questions/ask.html', {'form': form})

    else:
        # get是显示提问页面
        form = QuestionForm()

    return render(request, 'questions/ask.html', {'form': form})


@login_required
def question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    form = AnswerForm(initial={'question': question})
    return render(request, 'questions/question.html', {
        'question': question,
        'form': form
    })


@login_required
def answer(request):
    # 回答一个问题
    # post：提交答案
    # get：展示question
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            user = request.user
            answer = Answer()
            answer.user = request.user
            answer.question = form.cleaned_data.get('question')
            answer.description = form.cleaned_data.get('description')
            answer.save()

            # 发送通知
            user.profile.notify_answered(answer.question)
            return redirect(u'/questions/{0}/'.format(answer.question.pk))
        else:
            question = form.cleaned_data.get('question')
            return render(request, 'questions/question.html', {
                'question': question,
                'form': form
            })
    else:
        return redirect('/questions/')


@login_required
@ajax_required
def accept(request):
    # 接受某个答案为最终答案
    answer_id = request.POST['answer']
    answer = Answer.objects.get(pk=answer_id)
    user = request.user
    try:
        # answer.accept cleans previous accepted answer
        # 奇葩的逻辑：还可以再次accept
        # 也就是说，这里的话，如果提问者 觉得别的答案好，可以重新accept，那么这里需要clear之前的通知
        user.profile.unotify_accepted(answer.question.get_accepted_answer())

    except Exception, e:
        pass

    if answer.question.user == user:
        answer.accept()
        user.profile.notify_accepted(answer)
        return HttpResponse()

    else:
        return HttpResponseForbidden()


@login_required
@ajax_required
def vote(request):
    # 投票
    answer_id = request.POST['answer']
    answer = Answer.objects.get(pk=answer_id)
    vote = request.POST['vote']
    user = request.user

    # 投票主要是创建一个activity

    # 先查user在这个问题上之前的up／down的投票，并删掉
    activity = Activity.objects.filter(
        Q(activity_type=Activity.UP_VOTE) | Q(activity_type=Activity.DOWN_VOTE),
        user=user, answer=answer_id)
    if activity:
        activity.delete()

    # 创建一个新的投票activity
    if vote in [Activity.UP_VOTE, Activity.DOWN_VOTE]:
        activity = Activity(activity_type=vote, user=user, answer=answer_id)
        activity.save()
    return HttpResponse(answer.calculate_votes())


@login_required
@ajax_required
def favorite(request):
    # user 收藏question，处理方式同vote
    question_id = request.POST['question']
    question = Question.objects.get(pk=question_id)
    user = request.user
    activity = Activity.objects.filter(activity_type=Activity.FAVORITE,
                                       user=user, question=question_id)
    if activity:
        activity.delete()
        user.profile.unotify_favorited(question)
    else:
        activity = Activity(activity_type=Activity.FAVORITE, user=user,
                            question=question_id)
        activity.save()
        user.profile.notify_favorited(question)

    return HttpResponse(question.calculate_favorites())
