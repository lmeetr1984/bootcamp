# coding=utf-8
from django.shortcuts import render
from bootcamp.activities.models import Notification
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from bootcamp.decorators import ajax_required


@login_required
def notifications(request):
    # 显示所有的notifications
    user = request.user
    notifications = Notification.objects.filter(to_user=user)
    unread = Notification.objects.filter(to_user=user, is_read=False)
    for notification in unread:
        notification.is_read = True
        notification.save()

    return render(request, 'activities/notifications.html',
                  {'notifications': notifications})


@login_required
@ajax_required
def last_notifications(request):
    # 请求获取最新的5个未读通知
    user = request.user
    notifications = Notification.objects.filter(to_user=user,
                                                is_read=False)[:5]
    for notification in notifications:
        # 获取的同时，设置为已读
        notification.is_read = True
        notification.save()

    return render(request,
                  'activities/last_notifications.html',
                  {'notifications': notifications})


@login_required
@ajax_required
def check_notifications(request):
    # check 属于当前登陆用户最新的通知个数
    user = request.user
    notifications = Notification.objects.filter(to_user=user,
                                                is_read=False)[:5]
    return HttpResponse(len(notifications))
