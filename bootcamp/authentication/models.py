# coding:utf-8

import urllib
import hashlib
import os.path
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db import models
from django.conf import settings
from bootcamp.activities.models import Notification


# 用户的详细资料
class Profile(models.Model):
    # 和user是一对一关系
    user = models.OneToOneField(User)
    # 位置信息，允许为空，允许前台页面为空
    location = models.CharField(max_length=50, null=True, blank=True)
    url = models.CharField(max_length=50, null=True, blank=True)
    job_title = models.CharField(max_length=50, null=True, blank=True)

    # reputation = models.IntegerField(default=0)
    # language = models.CharField(max_length=5, default='en')

    class Meta:
        # 定义数据库表的名字
        db_table = 'auth_profile'

    def get_url(self):
        url = self.url
        # 如果url 不是http开头，增加一个头部
        if "http://" not in self.url and "https://" not in self.url and len(self.url) > 0:
            url = "http://" + str(self.url)

        return url

    def get_picture(self):
        # 获取头像
        no_picture = 'http://trybootcamp.vitorfs.com/static/img/user.png'

        try:
            # 构造头像的路径，文件名是 用户名
            filename = settings.MEDIA_ROOT + '/profile_pictures/' + self.user.username + '.jpg'
            # 构造头像的url
            picture_url = settings.MEDIA_URL + 'profile_pictures/' + self.user.username + '.jpg'

            # 如果文件存在，那么直接返回头像图像的url
            if os.path.isfile(filename):
                return picture_url
            else:
                # 否则的话，用gravatar服务声称一个
                gravatar_url = u'http://www.gravatar.com/avatar/{0}?{1}'.format(
                    hashlib.md5(self.user.email.lower()).hexdigest(),
                    urllib.urlencode({'d': no_picture, 's': '256'})
                )
                return gravatar_url

        except Exception, e:
            # 如果期间发生异常，则返回一个默认头像
            # 不应该做点儿什么？？比如log 
            return no_picture

    def get_screen_name(self):
        # 获取全名，如果有全名的话，那么返回全名，否则的话就返回username
        try:
            if self.user.get_full_name():
                return self.user.get_full_name()
            else:
                return self.user.username
        except:
            return self.user.username

    # 下面函数都是用来创建／取消通知的
    def notify_liked(self, feed):
        if self.user != feed.user:
            Notification(notification_type=Notification.LIKED,
                         from_user=self.user, to_user=feed.user,
                         feed=feed).save()

    def unotify_liked(self, feed):
        if self.user != feed.user:
            Notification.objects.filter(notification_type=Notification.LIKED,
                                        from_user=self.user, to_user=feed.user,
                                        feed=feed).delete()

    def notify_commented(self, feed):
        if self.user != feed.user:
            Notification(notification_type=Notification.COMMENTED,
                         from_user=self.user, to_user=feed.user,
                         feed=feed).save()

    def notify_also_commented(self, feed):
        comments = feed.get_comments()
        users = []
        for comment in comments:
            if comment.user != self.user and comment.user != feed.user:
                users.append(comment.user.pk)

        users = list(set(users))
        for user in users:
            Notification(notification_type=Notification.ALSO_COMMENTED,
                         from_user=self.user,
                         to_user=User(id=user), feed=feed).save()

    def notify_favorited(self, question):
        if self.user != question.user:
            Notification(notification_type=Notification.FAVORITED,
                         from_user=self.user, to_user=question.user,
                         question=question).save()

    def unotify_favorited(self, question):
        if self.user != question.user:
            Notification.objects.filter(
                notification_type=Notification.FAVORITED,
                from_user=self.user,
                to_user=question.user,
                question=question).delete()

    def notify_answered(self, question):
        if self.user != question.user:
            Notification(notification_type=Notification.ANSWERED,
                         from_user=self.user,
                         to_user=question.user,
                         question=question).save()

    def notify_accepted(self, answer):
        if self.user != answer.user:
            Notification(notification_type=Notification.ACCEPTED_ANSWER,
                         from_user=self.user,
                         to_user=answer.user,
                         answer=answer).save()

    def unotify_accepted(self, answer):
        if self.user != answer.user:
            Notification.objects.filter(
                notification_type=Notification.ACCEPTED_ANSWER,
                from_user=self.user,
                to_user=answer.user,
                answer=answer).delete()


# 注意函数签名
def create_user_profile(sender, instance, created, **kwargs):
    # 如果是创建动作，那么自动给用户创建一个Profile
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    # 一般用于保存（update）
    instance.profile.save()


# 定义了信号
# 当User 发生保存的动作之后，发送信号给create_user_profile 函数
post_save.connect(create_user_profile, sender=User)

# 当User 发生保存的动作之后，发送信号给save_user_profile 函数
post_save.connect(save_user_profile, sender=User)
