# coding=utf8
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from bootcamp.decorators import ajax_required
from django.contrib.auth.models import User
import json
from bootcamp.messenger.models import Message

# 打开个人收件箱

@login_required
def inbox(request):
    #获取某个人的所有会话列表
    conversations = Message.get_conversations(user=request.user)
    active_conversation = None
    messages = None
    if conversations:
        # 设置打开mailbox，先看哪个会话
        conversation = conversations[0]
        active_conversation = conversation['user'].username
        # 查询所有的这个active conversation的对话列表
        messages = Message.objects.filter(user=request.user,
                                          conversation=conversation['user'])
        messages.update(is_read=True)
        for conversation in conversations:
            if conversation['user'].username == active_conversation:
                conversation['unread'] = 0

    return render(request, 'messenger/inbox.html', {
        'messages': messages,
        'conversations': conversations,
        'active': active_conversation
        })


@login_required
def messages(request, username):
    # 获取登录用户 和 某个用户之间的conversation
    conversations = Message.get_conversations(user=request.user)
    active_conversation = username
    messages = Message.objects.filter(user=request.user,
                                      conversation__username=username)
    messages.update(is_read=True)
    for conversation in conversations:
        if conversation['user'].username == username:
            conversation['unread'] = 0

    return render(request, 'messenger/inbox.html', {
        'messages': messages,
        'conversations': conversations,
        'active': active_conversation
        })

# 发起一个新的会话
@login_required
def new(request):
    if request.method == 'POST':
        from_user = request.user
        to_user_username = request.POST.get('to')
        try:
            # 检查是否能查到to user的用户名
            to_user = User.objects.get(username=to_user_username)

        except Exception, e:
            # 处理了一下用户名，继续查
            try:
                to_user_username = to_user_username[
                    to_user_username.rfind('(')+1:len(to_user_username)-1]
                to_user = User.objects.get(username=to_user_username)

            except Exception, e:
                # 如果还查不到的话，那么就抛弃，直接返回到发送消息的页面
                return redirect('/messages/new/')

        message = request.POST.get('message')
        if len(message.strip()) == 0:
            # 如果空消息的话，那么直接返回到发送消息的页面
            return redirect('/messages/new/')

        if from_user != to_user:
            # from user 不等于 to user，才发送
            Message.send_message(from_user, to_user, message)

        # 跳转到当前用户和某个人的会话列表中
        return redirect(u'/messages/{0}/'.format(to_user_username))

    else:
        conversations = Message.get_conversations(user=request.user)
        return render(request, 'messenger/new.html',
                      {'conversations': conversations})


@login_required
@ajax_required
def delete(request):
    return HttpResponse()


@login_required
@ajax_required
def send(request):
    # 发送消息message
    if request.method == 'POST':
        from_user = request.user
        to_user_username = request.POST.get('to')
        # 根据用户名获取用户
        to_user = User.objects.get(username=to_user_username)
        message = request.POST.get('message')
        if len(message.strip()) == 0:
            return HttpResponse()

        # 收件人不能和发件人一样
        if from_user != to_user:
            # 构造messag，发送
            msg = Message.send_message(from_user, to_user, message)

            # 返回的是一段html渲染好的代码
            return render(request, 'messenger/includes/partial_message.html',
                          {'message': msg})

        return HttpResponse()
    else:
        # 如果是get请求，直接返回bad request
        # 注意这种写法
        return HttpResponseBadRequest()


@login_required
@ajax_required
def users(request):
    # ajax获取用户

    # 获取所有用户
    users = User.objects.filter(is_active=True)
    dump = []
    template = u'{0} ({1})'
    for user in users:
        if user.profile.get_screen_name() != user.username:
            dump.append(template.format(user.profile.get_screen_name(), user.username))
        else:
            dump.append(user.username)
    # dump json
    data = json.dumps(dump)

    # 返回json
    return HttpResponse(data, content_type='application/json')


@login_required
@ajax_required
def check(request):
    # 检查当前登陆用户的未读邮件的个数的
    count = Message.objects.filter(user=request.user, is_read=False).count()
    return HttpResponse(count)
