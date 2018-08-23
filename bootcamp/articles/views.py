# coding=utf-8

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponse
from bootcamp.articles.models import Article, Tag, ArticleComment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from bootcamp.articles.forms import ArticleForm
from django.contrib.auth.decorators import login_required
from bootcamp.decorators import ajax_required
import markdown
from django.template.loader import render_to_string


def _articles(request, articles):
    # 处理分页的
    paginator = Paginator(articles, 10)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    popular_tags = Tag.get_popular_tags()
    return render(request, 'articles/articles.html', {
        'articles': articles,
        'popular_tags': popular_tags
    })


@login_required
def articles(request):
    # 显示所有的发布文章
    all_articles = Article.get_published()
    return _articles(request, all_articles)


@login_required
def article(request, slug):
    # 获取某个具体的文章，用固定链接来处理
    article = get_object_or_404(Article, slug=slug, status=Article.PUBLISHED)
    return render(request, 'articles/article.html', {'article': article})


@login_required
def tag(request, tag_name):
    # 获取某个标签下的所有文章
    tags = Tag.objects.filter(tag=tag_name)
    articles = []
    for tag in tags:
        for article in tag.articles.all():
            if article.status == Article.PUBLISHED:
                articles.append(article)
    return _articles(request, articles)


@login_required
def write(request):
    # 提交文章
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = Article()
            article.create_user = request.user
            article.title = form.cleaned_data.get('title')
            article.content = form.cleaned_data.get('content')
            status = form.cleaned_data.get('status')
            if status in [Article.PUBLISHED, Article.DRAFT]:
                article.status = form.cleaned_data.get('status')
            article.save()
            tags = form.cleaned_data.get('tags')
            article.create_tags(tags)
            return redirect('/articles/')
    else:
        # get的话，就是打开编辑页面
        form = ArticleForm()
    return render(request, 'articles/write.html', {'form': form})


@login_required
def drafts(request):
    # 获取一个草稿
    drafts = Article.objects.filter(create_user=request.user,
                                    status=Article.DRAFT)
    return render(request, 'articles/drafts.html', {'drafts': drafts})


@login_required
def edit(request, id):
    # 编辑
    tags = ''
    if id:
        # 如果id存在的话，说明是update
        article = get_object_or_404(Article, pk=id)
        for tag in article.get_tags():
            tags = u'{0} {1}'.format(tags, tag.tag)
        tags = tags.strip()
    else:
        # 否则的话，是一个新文章
        article = Article(create_user=request.user)

    if article.create_user.id != request.user.id:
        # 如果修改者不是创建者的话，那么redirect到home
        return redirect('home')

    if request.POST:
        # 如果是post的话，那么获取表单数据，保存
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            # 这个方法根据表单绑定的数据创建并保存数据库对象
            form.save()
            return redirect('/articles/')
    else:
        # 否则的话，创建一个新的form，内容填充找到的内容，
        form = ArticleForm(instance=article, initial={'tags': tags})
    return render(request, 'articles/edit.html', {'form': form})


@login_required
@ajax_required
def preview(request):
    try:
        if request.method == 'POST':
            content = request.POST.get('content')
            html = 'Nothing to display :('
            if len(content.strip()) > 0:
                html = markdown.markdown(content, safe_mode='escape')
            return HttpResponse(html)
        else:
            return HttpResponseBadRequest()

    except Exception, e:
        return HttpResponseBadRequest()


@login_required
@ajax_required
def comment(request):
    try:
        if request.method == 'POST':
            article_id = request.POST.get('article')
            article = Article.objects.get(pk=article_id)
            comment = request.POST.get('comment')
            comment = comment.strip()
            if len(comment) > 0:
                article_comment = ArticleComment(user=request.user,
                                                 article=article,
                                                 comment=comment)
                article_comment.save()
            html = u''
            for comment in article.get_comments():
                html = u'{0}{1}'.format(html, render_to_string('articles/partial_article_comment.html',
                                                               {'comment': comment}))

            return HttpResponse(html)

        else:
            return HttpResponseBadRequest()

    except Exception, e:
        return HttpResponseBadRequest()
