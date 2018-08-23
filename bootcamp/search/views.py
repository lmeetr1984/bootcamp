# coding=utf8
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.models import User
from bootcamp.feeds.models import Feed
from bootcamp.articles.models import Article
from bootcamp.questions.models import Question
from django.contrib.auth.decorators import login_required


@login_required
def search(request):
    if 'q' in request.GET:
        querystring = request.GET.get('q').strip()
        if len(querystring) == 0:
            # 检索参数为空的话，那么直接跳转到search页面
            return redirect('/search/')

        try:
            # 如果请求中有type，用type，没有的话，用feed作为默认的type
            search_type = request.GET.get('type')
            if search_type not in ['feed', 'articles', 'questions', 'users']:
                search_type = 'feed'

        except Exception, e:
            search_type = 'feed'

        count = {}
        results = {}
        # 搜索主feed（feed parent＝None）
        results['feed'] = Feed.objects.filter(post__icontains=querystring,
                                              parent=None)

        # 检索文章， 主要检索文章的标题和内容
        results['articles'] = Article.objects.filter(
            Q(title__icontains=querystring) | Q(content__icontains=querystring)
            )

        # 检索问题， 检索标题，和描述
        results['questions'] = Question.objects.filter(
            Q(title__icontains=querystring) | Q(
                description__icontains=querystring))

        # 检索用户， 检索用户名 ， 姓 和 名
        results['users'] = User.objects.filter(
            Q(username__icontains=querystring) | Q(
                first_name__icontains=querystring) | Q(
                    last_name__icontains=querystring))

        # 分别计算了count
        count['feed'] = results['feed'].count()
        count['articles'] = results['articles'].count()
        count['questions'] = results['questions'].count()
        count['users'] = results['users'].count()

        # 渲染结果
        return render(request, 'search/results.html', {
            'hide_search': True, # 不显示base.html的检索条
            'querystring': querystring,
            'active': search_type,
            'count': count,
            'results': results[search_type],
        })
    else:
        # 不带q参数的话，那么就返回搜索页面
        return render(request, 'search/search.html', {'hide_search': True})
