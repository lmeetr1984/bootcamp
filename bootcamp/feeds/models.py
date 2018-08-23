# coding: utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from bootcamp.activities.models import Activity
from django.utils.html import escape
import bleach


class Feed(models.Model):
    # feed 作者
    user = models.ForeignKey(User)
    date = models.DateTimeField(auto_now_add=True)
    post = models.TextField(max_length=255)

    # 父feed
    parent = models.ForeignKey('Feed', null=True, blank=True)

    # 喜欢次数
    likes = models.IntegerField(default=0)

    # 评论数
    comments = models.IntegerField(default=0)

    class Meta:
        verbose_name = _('Feed')
        verbose_name_plural = _('Feeds')

        # 时间倒序
        ordering = ('-date',)

    def __unicode__(self):
        return self.post

    @staticmethod
    def get_feeds(from_feed=None):
        # 找到主feed，也就是没有parent的feed，这个方法主要是下拉分页用的
        if from_feed is not None:
            feeds = Feed.objects.filter(parent=None, id__lte=from_feed)
        else:
            # 找到主feed，也就是没有parent的feed
            feeds = Feed.objects.filter(parent=None)
        return feeds

    @staticmethod
    def get_feeds_after(feed):
        # 主要用于下拉刷新，用于找到id在某个feed之后的feed
        feeds = Feed.objects.filter(parent=None, id__gt=feed)
        return feeds

    def get_comments(self):
        # 获取当前feed的子feed（评论），按照日期顺序
        return Feed.objects.filter(parent=self).order_by('date')

    def calculate_likes(self):
        # 通过日志来计算like数目
        likes = Activity.objects.filter(activity_type=Activity.LIKE,
                                        feed=self.pk).count()
        self.likes = likes
        self.save()
        return self.likes

    def get_likes(self):
        # 通过日志来计算对feed喜欢的人
        likes = Activity.objects.filter(activity_type=Activity.LIKE,
                                        feed=self.pk)
        return likes

    def get_likers(self):
        likes = self.get_likes()
        likers = []
        for like in likes:
            likers.append(like.user)
        return likers

    def calculate_comments(self):
        # 计算评论的数目
        self.comments = Feed.objects.filter(parent=self).count()
        self.save()
        return self.comments

    def comment(self, user, post):
        # 就当前的feed，发表评论
        # 构造一个feed， 
        feed_comment = Feed(user=user, post=post, parent=self)
        feed_comment.save()

        # 增加当前的评论数计数， 保存
        self.comments = Feed.objects.filter(parent=self).count()
        self.save()
        return feed_comment

    def linkfy_post(self):
        # 使用bleach来安全的处理post内容，去除掉各种转义符号
        return bleach.linkify(escape(self.post))
