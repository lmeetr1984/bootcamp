# coding: utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models import Max


# 站内消息
class Message(models.Model):
    # 所属人。属于谁的mailbox
    user = models.ForeignKey(User, related_name='+')
    # 内容
    message = models.TextField(max_length=1000, blank=True)
    # 日期
    # auto_now_add:当对象第一次被创建时自动设置当前时间
    date = models.DateTimeField(auto_now_add=True)

    # 会话，也就是和某个用户 的一系列对话
    # related_name: 这个名称用于让关联的对象反查到源对象。
    # 如果你不想让Django 创建一个反向关联，请设置related_name 为 '+' 或者以'+' 结尾。
    # 因为User是内置对象，这样就不会给User增加新的属性了，很重要！
    conversation = models.ForeignKey(User, related_name='+')
    # 标记该条message 是来自哪个人的（有可能是自己，有可能是其他人）
    from_user = models.ForeignKey(User, related_name='+')
    is_read = models.BooleanField(default=False)

    class Meta:
        # verbose也用了国际化
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        # 排序用date升序
        ordering = ('date',)
        # 数据库表名
        db_table = 'messages_message'

    def __unicode__(self):
        return self.message

    @staticmethod
    def send_message(from_user, to_user, message):
        # 发送消息
        # 最大的字数是1000
        message = message[:1000]

        # 先构造一个自己 mailbox 的 message
        # 自己mailbox的阅读状态是已读
        current_user_message = Message(from_user=from_user,
                                       message=message,
                                       user=from_user,
                                       conversation=to_user,
                                       is_read=True)
        current_user_message.save()

        # 在构造一个对方mailbox的message
        Message(from_user=from_user,
                conversation=from_user,
                message=message,
                user=to_user).save()

        return current_user_message

    @staticmethod
    def get_conversations(user):
        # 获取某个用户mailbox中的对话列表

        # 首先找到所有的user mailbox的message
        # values : 只获取所有的converstation的值， 以[{},{},...]给出
        # annotate: 增加一个新的列，列名＝last，value＝最新的日期

        # 下面代码：获取user的message，然后只拿coversation数据
        # annotate 新增加了一列，叫做last，只当前coverstion的最后更新时间
        # 然后排序
        # 实际上实现了sql的
        # select conversation, max(date) last from message group by conversation order by last
        conversations = Message.objects.filter(
            user=user).values('conversation').annotate(
                last=Max('date')).order_by('-last')
        users = []
        for conversation in conversations:
            users.append({
                'user': User.objects.get(pk=conversation['conversation']),
                'last': conversation['last'],
                'unread': Message.objects.filter(user=user,
                                                 conversation__pk=conversation[
                                                    'conversation'],
                                                 is_read=False).count(),
                })

        return users
