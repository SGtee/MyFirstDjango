from django.shortcuts import render
from .models import Post,Category
from django.shortcuts import render,get_object_or_404
import markdown
from comments.forms import CommentForm
from django.db.models.aggregates import Count
from django.views.generic import ListView,DetailView

from django.http import HttpResponse
# Create your views here.

"""def index(requst):
    post_list=Post.objects.all().order_by('-created_time')
    return render(requst,'blog/index.html',context={
        'post_list':post_list
    })
"""
#把视图函数改写为类函数，以减少视图函数重复代码，节省开发时间
class IndexView(ListView):
    model = Post #将model指定为Post,获取Post模型
    template_name = 'blog/index.html' #指定渲染的模板
    context_object_name = 'post_list' #指定获取的模型列表数据保存的变量名，这个变量会传递给模板

'''
def detail(requst,pk):
    post=get_object_or_404(Post,pk=pk)

    #阅读量+1
    post.increase_views()

    post.body=markdown.markdown(post.body,
                                extensions=[
                                    'markdown.extensions.extra',
                                    'markdown.extensions.codehilite',
                                    'markdown.extensions.toc'
                                ])
    form=CommentForm()
    comment_list=post.comment_set.all()
    context={'post':post,
             'form':form,
             'comment_list':comment_list}
    return  render(requst,'blog/detail.html',context=context)
'''
class PostDetailView(DetailView):
    #这些属性和ListView是一样的
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        #覆写get方法的原因是因为每当文章被访问一次，就得将文章访问数+1
        #get方法返回的是一个HTTPresponse实例
        #之所以先要调用父类的get方法，是因为只有当get方法调用后
        #才有self.object属性，其值为Post模型实例，即被访问的文章post
        response=super(PostDetailView,self).get(request,*args,*kwargs)

        #将文章浏览数+1
        #注意self.object的值就是被访问的文章post
        self.object.increase_views()

        #视图必须返回一个httpresponse对象
        return response

    def get_object(self, queryset=None):
        #覆写get_object的目的是因为需要对post的body值进行渲染
        post=super(PostDetailView,self).get_object(queryset=None)
        post.body=markdown.markdown(post.body,
                                    extensions=[
                                        'markdown.extensions.extra',
                                        'markdown.extensions.codehilite',
                                        'markdown.extensions.toc',
                                    ])
        return post

    def get_context_data(self, **kwargs):
        #覆写get_context_data的目的是因为除了将post的值传递给模板外（DetailView已经帮我们完成）
        #还要把评论表单、post下的评论列表传递给模板
        context=super(PostDetailView,self).get_context_data(**kwargs)
        form=CommentForm()
        comment_list=self.object.comment_set.all()
        context.update({
            'form':form,
            'comment_list':comment_list,
        })
        return context
class CategoryView(IndexView):
    def get_queryset(self):#get_queryset()方法默认获取指定模型的全部列表数据
        cate=get_object_or_404(Category,pk=self.kwargs.get('pk'))
        #在类视图中，从 URL 捕获的命名组参数值保存在实例的 kwargs 属性（是一个字典）里，
        # 非命名组参数值保存在实例的 args 属性（是一个列表）里。
        return super(CategoryView, self).get_queryset().filter(category=cate)
'''
def archives(request,year,month):
    post_list=Post.objects.filter(created_time__year=year,
                                  created_time__month=month).order_by('-created_time')
    return render(request,'blog/index.html',context={
        'post_list':post_list
    })
'''
class ArchivesViews(IndexView):
    def get_queryset(self):
        year=self.kwargs.get('year')
        month=self.kwargs.get('month')
        return super(ArchivesViews,self).get_queryset().filter(created_time__year=year,
                                                               created_time__month=month).order_by('-created_time')
'''def category(request,pk):
    cate=get_object_or_404(Category,pk=pk)
    # category_list=Category.objects.annotate(num_posts=Count('post'))
    post_list=Post.objects.filter(category=cate).order_by('-created_time')
    return render(request,'blog/index.html',context={'post_list':post_list,
                                                     })
'''
def search(request):
    q=request.GET.get('q')
    error_msg=''

    if not q:
        error_msg='请输入关键词'
        return render(request,'blog/index.html',{'error_msg':error_msg,
                                                  })
    post_list=Post.objects.filter(title__icontains=q)
    return render(request,'blog/index.html',{'error_msg':error_msg,
                                               'post_list':post_list,
                                             })