from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.six import python_2_unicode_compatible
from django.utils.html import strip_tags

# Create your models here.
@python_2_unicode_compatible
class Category(models.Model):
    name=models.CharField(max_length=100)

@python_2_unicode_compatible
class Tag(models.Model):
    name=models.CharField(max_length=100)

@python_2_unicode_compatible
class Post(models.Model):
    title=models.CharField(max_length=70)
    body=models.TextField()
    created_time=models.DateTimeField()
    modified_time=models.DateTimeField()
    excerpt=models.CharField(max_length=200,blank=True)

    category=models.ForeignKey(Category)
    tags=models.ManyToManyField(Tag,blank=True)
    author=models.ForeignKey(User)

    #新增views字段记录阅读量
    views=models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail',kwargs={'pk':self.pk})

    #增加模型方法
    def increase_views(self):
        self.views+=1
        self.save(update_fields=['views'])

    #自动生成文章摘要
    def save(self,*args,**kwargs):
        #如果没有填写摘要
        if not self.excerpt:
            #首先实例化一个markdown类，用于渲染body的文本
            md=markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
            ])
            # 先将 Markdown 文本渲染成 HTML 文本
            # strip_tags 去掉 HTML 文本的全部 HTML 标签
            # 从文本摘取前 54 个字符赋给 excerpt
            self.excerpt=strip_tags(md.convert(self.body))[:54]

            #调用父类的save方法将数据保存到数据库中
        super(Post,self).save(*args,**kwargs)