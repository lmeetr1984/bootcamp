# coding=utf-8

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseForbidden
from bootcamp.feeds.models import Feed
from bootcamp.activities.models import Activity
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.template.context_processors import csrf
import json
from django.contrib.auth.decorators import login_required
from bootcamp.decorators import ajax_required

# 每页显示10个feed
FEEDS_NUM_PAGES = 10


@login_required
def feeds(request):
    # 查看所有的主feed
    all_feeds = Feed.get_feeds()

    #分页，一次10个
    paginator = Paginator(all_feeds, FEEDS_NUM_PAGES)

    # 第一次加载，获取第一页
    feeds = paginator.page(1)
    from_feed = -1
    if feeds:
        from_feed = feeds[0].id
    return render(request, 'feeds/feeds.html', {
        'feeds': feeds,
        'from_feed': from_feed,
        'page': 1,
    })


def feed(request, pk):
    feed = get_object_or_404(Feed, pk=pk)
    return render(request, 'feeds/feed.html', {'feed': feed})


@login_required
@ajax_required
def load(request):
    # 加载分页数据
    from_feed = request.GET.get('from_feed')
    page = request.GET.get('page')
    feed_source = request.GET.get('feed_source')

    # 从from_feed开始获取主feed
    all_feeds = Feed.get_feeds(from_feed)
    if feed_source != 'all':
        all_feeds = all_feeds.filter(user__id=feed_source)

    # 分页
    paginator = Paginator(all_feeds, FEEDS_NUM_PAGES)
    try:
        feeds = paginator.page(page)
    except PageNotAnInteger:
        return HttpResponseBadRequest()
    except EmptyPage:
        feeds = []
    html = u''

    # 重新计算一个csrftoken
    csrf_token = unicode(csrf(request)['csrf_token'])

    # 渲染一下
    # render_to_string: 用模版去format，返回string
    # 循环渲染，返回的是所有的feed的html string
    # 用于ajax append 到节点上
    for feed in feeds:
        html = u'{0}{1}'.format(html,
                                render_to_string('feeds/partial_feed.html',
                                                 {
                                                     'feed': feed,
                                                     'user': request.user,
                                                     'csrf_token': csrf_token
                                                 }))

    return HttpResponse(html)


def _html_feeds(last_feed, user, csrf_token, feed_source='all'):
    feeds = Feed.get_feeds_after(last_feed)
    if feed_source != 'all':
        feeds = feeds.filter(user__id=feed_source)
    html = u''
    for feed in feeds:
        html = u'{0}{1}'.format(html,
                                render_to_string('feeds/partial_feed.html',
                                                 {
                                                     'feed': feed,
                                                     'user': user,
                                                     'csrf_token': csrf_token
                                                 }))

    return html


@login_required
@ajax_required
def load_new(request):
    last_feed = request.GET.get('last_feed')
    user = request.user
    csrf_token = unicode(csrf(request)['csrf_token'])
    html = _html_feeds(last_feed, user, csrf_token)
    return HttpResponse(html)


@login_required
@ajax_required
def check(request):
    # 检查是否有新的feed
    # 从页面中获取最新的feed id
    last_feed = request.GET.get('last_feed')
    feed_source = request.GET.get('feed_source')
    feeds = Feed.get_feeds_after(last_feed)
    if feed_source != 'all':
        feeds = feeds.filter(user__id=feed_source)
    count = feeds.count()
    return HttpResponse(count)


@login_required
@ajax_required
def post(request):
    last_feed = request.POST.get('last_feed')
    user = request.user
    csrf_token = unicode(csrf(request)['csrf_token'])
    feed = Feed()
    feed.user = user
    post = request.POST['post']
    post = post.strip()
    if len(post) > 0:
        feed.post = post[:255]
        feed.save()
    html = _html_feeds(last_feed, user, csrf_token)
    return HttpResponse(html)


@login_required
@ajax_required
def like(request):
    "点击like 的 view"

    # 获取 被点赞的feed id
    feed_id = request.POST['feed']

    # 获取feed
    feed = Feed.objects.get(pk=feed_id)

    # 获取当前的登陆用户
    user = request.user

    # 查找是否这个用户以前点过赞
    like = Activity.objects.filter(activity_type=Activity.LIKE, feed=feed_id,
                                   user=user)
    if like:
        # 如果点过赞，删除notifications
        user.profile.unotify_liked(feed)
        # 删除这个点赞记录
        like.delete()

    else:
        # 创建一个赞
        like = Activity(activity_type=Activity.LIKE, feed=feed_id, user=user)
        like.save()
        user.profile.notify_liked(feed)

    return HttpResponse(feed.calculate_likes())


@login_required
@ajax_required
def comment(request):
    # 评论
    if request.method == 'POST':
        feed_id = request.POST['feed']
        feed = Feed.objects.get(pk=feed_id)
        post = request.POST['post']
        post = post.strip()
        if len(post) > 0:
            # 评论最大是255个
            post = post[:255]
            user = request.user
            feed.comment(user=user, post=post)

            # notify 发通知
            user.profile.notify_commented(feed)
            user.profile.notify_also_commented(feed)
        return render(request, 'feeds/partial_feed_comments.html',
                      {'feed': feed})

    else:
        feed_id = request.GET.get('feed')
        feed = Feed.objects.get(pk=feed_id)
        return render(request, 'feeds/partial_feed_comments.html',
                      {'feed': feed})


@login_required
@ajax_required
def update(request):
    first_feed = request.GET.get('first_feed')
    last_feed = request.GET.get('last_feed')
    feed_source = request.GET.get('feed_source')
    feeds = Feed.get_feeds().filter(id__range=(last_feed, first_feed))
    if feed_source != 'all':
        feeds = feeds.filter(user__id=feed_source)
    dump = {}
    for feed in feeds:
        dump[feed.pk] = {'likes': feed.likes, 'comments': feed.comments}
    data = json.dumps(dump)
    return HttpResponse(data, content_type='application/json')


@login_required
@ajax_required
def track_comments(request):
    # 检查新的评论
    feed_id = request.GET.get('feed')
    feed = Feed.objects.get(pk=feed_id)
    return render(request, 'feeds/partial_feed_comments.html', {'feed': feed})


@login_required
@ajax_required
def remove(request):
    # 删除一个feed
    try:
        feed_id = request.POST.get('feed')
        feed = Feed.objects.get(pk=feed_id)

        # 必须是自己才能删除
        if feed.user == request.user:
            likes = feed.get_likes()
            parent = feed.parent

            # 顺便删除所有的like记录
            for like in likes:
                like.delete()
            feed.delete()

            #重新计算parent的评论数
            if parent:
                parent.calculate_comments()
            return HttpResponse()
        else:
            return HttpResponseForbidden()
    except Exception, e:
        return HttpResponseBadRequest()
