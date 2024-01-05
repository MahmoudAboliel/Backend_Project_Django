from django.shortcuts import render, get_object_or_404
from . import models
from . import forms
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.views.decorators.http import require_POST

# Create your views here.

### Building Function Based Views ###

# def post_list(request):
#     posts_list = models.Post.objects.all()
#     paginator = Paginator(posts_list, 3)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.page(page_number)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
#     except PageNotAnInteger:
#         posts = paginator.page(1)

#     return render(request, 'blog/post/list.html', {'posts': posts})

### Building Class Based Views ###
class PostListViews(ListView):
    model = models.Post
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    # method 1
    # try:
    #     post = models.Post.objects.get(id=id)
    # except models.Post.DoesNotExist:
    #     raise Http404('No Post Found')
    # return render(request, 'blog/post/detail.html', {'post':post})

    # method 2
    post = get_object_or_404(
        models.Post,
        status=models.Post.Status.PUBLISHED,
        publish__year=year,
        publish__month=month,
        publish__day=day,
        slug=post
    )
    return render(request, 'blog/post/detail.html', {'post': post})


def post_share(request, post_id):
    post = get_object_or_404(models.Post, id=post_id, status=models.Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        # Form was submitted
        form = forms.EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url} \n {cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'maboliel1998@gmail.com', [cd['to']])
            sent = True
            # ... send email
    else:
        form = forms.EmailPostForm()
        
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


# method type just POST
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(models.Post, id=post_id, status=models.Post.Status.PUBLISHED)
    comment = None
    
    form = forms.CommentForm(data=request.POST)
    if form.is_valid():
        #create a comment object without saving it to the database
        comment = form.save(commit=False)
        #Assign the post to the comment
        comment.post = post
        
        comment.save()
        
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})