# coding=utf-8

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from bootcamp.authentication.forms import SignUpForm
from django.contrib.auth.models import User
from bootcamp.feeds.models import Feed


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)

        # 首先用POST数据初始化一个form，如果form数据校验不通过，那么返回页面
        # form instance会带错误信息
        if not form.is_valid():
            return render(request, 'authentication/signup.html',
                          {'form': form})

        else:
            # 获取form的数据，必须用cleaned_data
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # 创建一个auth.User用户
            User.objects.create_user(username=username, password=password,
                                     email=email)

            # authenticate方法：负责用账号密码通过验证，如果验证通过，返回一个user
            user = authenticate(username=username, password=password)

            # 注册用户直接登陆，就是把用户绑定到request中
            login(request, user)

            # 发送一个welcome feed
            welcome_post = u'{0} has joined the network.'.format(user.username,
                                                                 user.username)
            feed = Feed(user=user, post=welcome_post)
            feed.save()

            # 跳转到主页
            return redirect('/')

    else:
        # 返回注册页面
        return render(request, 'authentication/signup.html',
                      {'form': SignUpForm()})
