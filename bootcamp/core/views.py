# coding: utf-8

import os
from PIL import Image

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings as django_settings
from django.shortcuts import render, redirect, get_object_or_404

from bootcamp.core.forms import ProfileForm, ChangePasswordForm
from bootcamp.feeds.models import Feed
from bootcamp.feeds.views import FEEDS_NUM_PAGES
from bootcamp.feeds.views import feeds


# 首页校验规则： 如果登录了，则重定向到feeds()这个请求, 否则显示(渲染)登录页面
# 每个请求上提供一个request.user属性，表示当前的用户。如果当前的用户没有登入，
# 该属性将设置成AnonymousUser的一个实例，否则它将是User的实例。
def home(request):
    if request.user.is_authenticated():
        # 注意这个写法，没有用redirect便捷函数
        return feeds(request)
    else:
        return render(request, 'core/cover.html')


# login_required装饰器：
# 1. 如果用户没有登入，则重定向到settings.LOGIN_URL，并传递当前查询字符串中的绝对路径。
# 2. 如果用户已经登入，则正常执行视图。视图的代码可以安全地假设用户已经登入。
@login_required
def network(request):
    # 获取所有激活用户，按照username排序
    users_list = User.objects.filter(is_active=True).order_by('username')

    # http://python.usyiyi.cn/django/topics/pagination.html
    # 100个元素一页
    # 这个时候也没有执行查询的，等到真正使用的时候，开始构造查询sql
    # sql中会加入limit 1, 100 这样的语句，所以性能是可以的
    # 当然缓存的性能更好
    paginator = Paginator(users_list, 100)

    # 获取request中的当前页数
    page = request.GET.get('page')

    try:
        # 调取page页，这个时候并没有执行数据库查询
        users = paginator.page(page)
    except PageNotAnInteger:
        # 找不到页的话，或者page不是一个int,  就返回第一页
        users = paginator.page(1)
    except EmptyPage:
        # 如果当前页不包含数据的话，那么返回最后一页
        users = paginator.page(paginator.num_pages)
    return render(request, 'core/network.html', {'users': users})


@login_required
def profile(request, username):
    # 获取用户的profile

    # 根据用户名找到用户， 否则一个404
    page_user = get_object_or_404(User, username=username)

    # 找到该用户的所有feed
    all_feeds = Feed.get_feeds().filter(user=page_user)
    # 获取10个
    paginator = Paginator(all_feeds, FEEDS_NUM_PAGES)
    feeds = paginator.page(1)
    from_feed = -1
    if feeds:
        from_feed = feeds[0].id

    # 用模版填充渲染，和flask没有什么区别
    return render(request, 'core/profile.html', {
        'page_user': page_user,
        'feeds': feeds,
        'from_feed': from_feed,
        'page': 1
    })


@login_required
def settings(request):
    # 因为已经登录了，所以从request中可以去的user
    user = request.user
    if request.method == 'POST':
        # 处理表单保存
        # 用post过来的属性 初始化一个form
        form = ProfileForm(request.POST)
        # 如果form合法的话
        if form.is_valid():
            # cleaned_data 获取合法数据
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')

            # profile  关联到 user ， 一对一
            user.profile.job_title = form.cleaned_data.get('job_title')
            user.email = form.cleaned_data.get('email')
            user.profile.url = form.cleaned_data.get('url')
            user.profile.location = form.cleaned_data.get('location')

            # 因为设置了信号，所以保存user就可以了
            user.save()

            # 创建一个flash message， 告诉已经成功创建
            messages.add_message(request,
                                 messages.SUCCESS,
                                 'Your profile was successfully edited.')

    else:
        # 如果是get方法的话， 初始化一个默认的form 
        form = ProfileForm(instance=user, initial={
            'job_title': user.profile.job_title,
            'url': user.profile.url,
            'location': user.profile.location
        })

    # 用form去渲染html
    return render(request, 'core/settings.html', {'form': form})


# 打开个人头像的网页
@login_required
def picture(request):
    uploaded_picture = False
    try:
        if request.GET.get('upload_picture') == 'uploaded':
            uploaded_picture = True

    except Exception, e:
        pass

    return render(request, 'core/picture.html',
                  {'uploaded_picture': uploaded_picture})


@login_required
def password(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            user.set_password(new_password)
            user.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Your password was successfully changed.')

    else:
        form = ChangePasswordForm(instance=user)

    return render(request, 'core/password.html', {'form': form})


# 当用户想要修改头像的时候，首先做的第一件事情是把图片上传到服务器上
@login_required
def upload_picture(request):
    try:
        profile_pictures = django_settings.MEDIA_ROOT + '/profile_pictures/'

        # 目录不存在，创建一个
        if not os.path.exists(profile_pictures):
            os.makedirs(profile_pictures)

        # 获取上传文件的字段
        f = request.FILES['picture']

        # 构造文件的路径
        filename = profile_pictures + request.user.username + '_tmp.jpg'

        # 保存文件
        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)

        # 保存完毕，用PIL打开文件图片
        im = Image.open(filename)
        # 获取
        width, height = im.size
        if width > 350:
            new_width = 350
            new_height = (height * 350) / width
            new_size = new_width, new_height
            im.thumbnail(new_size, Image.ANTIALIAS)
            im.save(filename)
        # 重定向， 因为重定向在request中的参数是带不过去的，
        # 这里通过对url加参数， 把参数带过去
        return redirect('/settings/picture/?upload_picture=uploaded')

    except Exception, e:
        print e
        # 如果编辑图像的时候出现了某种异常，或者保存图片的时候出现某种异常，
        # 返回到图片编辑页面
        return redirect('/settings/picture/')


@login_required
def save_uploaded_picture(request):
    try:
        x = int(request.POST.get('x'))
        y = int(request.POST.get('y'))
        w = int(request.POST.get('w'))
        h = int(request.POST.get('h'))

        # 头像名称以用户名 命名
        tmp_filename = django_settings.MEDIA_ROOT + '/profile_pictures/' + request.user.username + '_tmp.jpg'
        filename = django_settings.MEDIA_ROOT + '/profile_pictures/' + request.user.username + '.jpg'
        im = Image.open(tmp_filename)
        cropped_im = im.crop((x, y, w + x, h + y))
        cropped_im.thumbnail((200, 200), Image.ANTIALIAS)
        cropped_im.save(filename)
        os.remove(tmp_filename)

    except Exception, e:
        pass

    return redirect('/settings/picture/')
