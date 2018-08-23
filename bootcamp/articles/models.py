# coding=utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from datetime import datetime
from django.template.defaultfilters import slugify
import markdown


class Article(models.Model):
    DRAFT = 'D'
    PUBLISHED = 'P'

    # 文章状态choice
    STATUS = (
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
    )

    title = models.CharField(max_length=255)

    # 文章的固定链接
    slug = models.SlugField(max_length=255, null=True, blank=True)
    content = models.TextField(max_length=4000)
    status = models.CharField(max_length=1, choices=STATUS, default=DRAFT)
    create_user = models.ForeignKey(User)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True)
    update_user = models.ForeignKey(User, null=True, blank=True,
                                    related_name="+")

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ("-create_date",)

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.pk:
            # 如果是保存的话
            super(Article, self).save(*args, **kwargs)
        else:
            # 如果是更新的话
            # 作者不知道用auto_now 选项？
            self.update_date = datetime.now()
        if not self.slug:
            # 如果短链接不存在的话
            # 构建短链接 pk title
            # slugify 会把空格变成横线
            slug_str = "%s %s" % (self.pk, self.title.lower())
            self.slug = slugify(slug_str)
        super(Article, self).save(*args, **kwargs)

    def get_content_as_markdown(self):
        return markdown.markdown(self.content, safe_mode='escape')

    @staticmethod
    def get_published():
        articles = Article.objects.filter(status=Article.PUBLISHED)
        return articles

    def create_tags(self, tags):
        tags = tags.strip()
        tag_list = tags.split(' ')
        for tag in tag_list:
            if tag:
                # 查询到了，就用查询的，否则就创建一个
                t, created = Tag.objects.get_or_create(tag=tag.lower())
                t.articles.add(self)

    def get_tags(self):
        return self.tag_set.all()

    def get_summary(self):
        if len(self.content) > 255:
            return u'{0}...'.format(self.content[:255])
        else:
            return self.content

    def get_summary_as_markdown(self):
        return markdown.markdown(self.get_summary(), safe_mode='escape')

    def get_comments(self):
        return ArticleComment.objects.filter(article=self)


class Tag(models.Model):
    "标签，和question的标签处理方法一样"
    tag = models.CharField(max_length=50)

    # 作者以前是1对多，我给改成多对多
    # 一对多会有问题的
    articles = models.ManyToManyField(Article)

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        # unique_together = (('tag', 'article'),)
        # index_together = [['tag', 'article'], ]

    def __unicode__(self):
        return self.tag

    @staticmethod
    def get_popular_tags():
        tags = Tag.objects.all()
        count = {}
        for tag in tags:
            for article in tag.articles.all():
                if article.status == Article.PUBLISHED:
                    if tag.tag in count:
                        count[tag.tag] = count[tag.tag] + 1
                    else:
                        count[tag.tag] = 1
        sorted_count = sorted(count.items(), key=lambda t: t[1], reverse=True)
        return sorted_count[:20]


class ArticleComment(models.Model):
    # 评论， 一对多
    article = models.ForeignKey(Article)
    comment = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)

    class Meta:
        verbose_name = _("Article Comment")
        verbose_name_plural = _("Article Comments")
        ordering = ("date",)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.user.username, self.article.title)
