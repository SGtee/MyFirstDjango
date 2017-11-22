from django.shortcuts import render
from .models import Post,Category
from django.shortcuts import render,get_object_or_404
import markdown
from comments.forms import CommentForm
from django.db.models.aggregates import Count

from django.http import HttpResponse
# Create your views here.

def index(requst):
    post_list=Post.objects.all().order_by('-created_time')
    return render(requst,'blog/index.html',context={
        'post_list':post_list
    })

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

def archives(request,year,month):
    post_list=Post.objects.filter(created_time__year=year,
                                  created_time__month=month).order_by('-created_time')
    return render(request,'blog/index.html',context={
        'post_list':post_list
    })

def category(request,pk):
    cate=get_object_or_404(Category,pk=pk)
    # category_list=Category.objects.annotate(num_posts=Count('post'))
    post_list=Post.objects.filter(category=cate).order_by('-created_time')
    return render(request,'blog/index.html',context={'post_list':post_list,
                                                     })
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