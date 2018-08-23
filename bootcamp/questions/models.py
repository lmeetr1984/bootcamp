# coding:utf-8

from django.db import models
from django.contrib.auth.models import User
from bootcamp.activities.models import Activity
import markdown


class Question(models.Model):
    # 一对多，一个用户可以有多个问题
    user = models.ForeignKey(User)

    # 问题title
    title = models.CharField(max_length=255)

    # 描述，最长2000
    description = models.TextField(max_length=2000)

    # 创建时间
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now_add=True)

    # 喜欢的次数
    favorites = models.IntegerField(default=0)

    # 该问题是否已经有答案被接受了，bool型
    has_accepted_answer = models.BooleanField(default=False)

    class Meta:
        # 对象的一个易于理解的名称
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

        # 对象默认的顺序，获取一个对象的列表时使用：
        ordering = ('-update_date',)

    def __unicode__(self):
        return self.title

    # 可以看到，类方法是处理获取多个对象的
    # instance方法：处理单个对象的
    @staticmethod
    def get_unanswered():
        return Question.objects.filter(has_accepted_answer=False)

    @staticmethod
    def get_answered():
        return Question.objects.filter(has_accepted_answer=True)

    def get_answers(self):
        # 获取某个问题的答案，注意使用self作为参数
        return Answer.objects.filter(question=self)

    def get_answers_count(self):
        return Answer.objects.filter(question=self).count()

    def get_accepted_answer(self):
        # 获取当前问题的accept答案
        return Answer.objects.get(question=self, is_accepted=True)

    def get_description_as_markdown(self):
        # 获取markdown
        return markdown.markdown(self.description, safe_mode='escape')

    def get_description_preview(self):
        # preview(在问题列表中显示的)最大值255
        if len(self.description) > 255:
            return u'{0}...'.format(self.description[:255])
        else:
            return self.description

    def get_description_preview_as_markdown(self):
        # 把markdown 格式转换成html格式
        return markdown.markdown(self.get_description_preview(),
                                 safe_mode='escape')

    def calculate_favorites(self):
        favorites = Activity.objects.filter(activity_type=Activity.FAVORITE,
                                            question=self.pk).count()
        self.favorites = favorites
        self.save()
        return self.favorites

    def get_favoriters(self):
        favorites = Activity.objects.filter(activity_type=Activity.FAVORITE,
                                            question=self.pk)
        favoriters = []
        for favorite in favorites:
            favoriters.append(favorite.user)
        return favoriters

    def create_tags(self, tags):
        # 创建标签
        tags = tags.strip()
        # tag以空格分割
        tag_list = tags.split(' ')

        for tag in tag_list:
            # 如果存在获取，否则保存
            # 因为这里用了tag 和 question 一起查找，所以，每次都需要创建
            t, created = Tag.objects.get_or_create(tag=tag.lower())

            # add 不需要再save，直接保存关系
            t.questions.add(self)

    def get_tags(self):
        # 获取tag，没有用复杂的多对多方式
        # 这里会不会出现问题？就是同名的标签重复？
        # 测试了，会有重复标签，或许作者就这样设计的
        # return Tag.objects.filter(question=self)

        return self.tag_set.all()


class Answer(models.Model):
    user = models.ForeignKey(User)
    # 问题的答案， 1对多设计
    # 一个问题对应多个答案
    question = models.ForeignKey(Question)
    description = models.TextField(max_length=2000)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(null=True, blank=True)
    votes = models.IntegerField(default=0)

    # 该问题是否被采纳
    is_accepted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'
        # 排序 首先根据 是否接受的答案，被接受次数最多的答案，创建时间
        ordering = ('-is_accepted', '-votes', 'create_date',)

    def __unicode__(self):
        return self.description

    def accept(self):
        # 接受答案（动作）
        # 首先根据当前的答案关联的question，找到所有的answer
        answers = Answer.objects.filter(question=self.question)

        # 把所有的关联答案全部设成false
        for answer in answers:
            answer.is_accepted = False
            answer.save()

        # 当前答案设为接受
        self.is_accepted = True
        # 保存
        self.save()
        # 设置关联的question，为接受
        self.question.has_accepted_answer = True
        # 保存
        self.question.save()

    def calculate_votes(self):
        # 依然是从日志中计算投票的次数
        up_votes = Activity.objects.filter(activity_type=Activity.UP_VOTE,
                                           answer=self.pk).count()
        down_votes = Activity.objects.filter(activity_type=Activity.DOWN_VOTE,
                                             answer=self.pk).count()

        # 投票：up投票 - down投票
        self.votes = up_votes - down_votes
        self.save()
        return self.votes

    def get_up_voters(self):
        # 获取该答案的up投票
        votes = Activity.objects.filter(activity_type=Activity.UP_VOTE,
                                        answer=self.pk)
        voters = []
        for vote in votes:
            voters.append(vote.user)
        return voters

    def get_down_voters(self):
        # 获取该问题的down投票
        votes = Activity.objects.filter(activity_type=Activity.DOWN_VOTE,
                                        answer=self.pk)
        voters = []
        for vote in votes:
            voters.append(vote.user)
        return voters

    def get_description_as_markdown(self):
        return markdown.markdown(self.description, safe_mode='escape')


class Tag(models.Model):
    "标签"
    tag = models.CharField(max_length=50)
    # 原文是一对多，我修改成多对多
    questions = models.ManyToManyField(Question)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        # 设置唯一键索引
        # unique_together = (('tag', 'question'),)
        # 设置组合索引
        # index_together = [['tag', 'question'], ]

    def __unicode__(self):
        return self.tag
