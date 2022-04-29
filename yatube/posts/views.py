from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from posts import forms, models


def index(request):
    post_list = models.Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    index = {
        'page': page
    }
    return render(request, 'index.html', index)


def group_posts(request, slug):
    group = get_object_or_404(models.Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    group_posts = {
        'group': group,
        'page': page,
    }
    return render(request, 'group.html', group_posts)


def profile(request, username):
    author = get_object_or_404(models.User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = request.user.is_authenticated and (
        models.Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    )
    profile = {
        'author': author,
        'page': page,
        'following': following,
    }
    return render(request, 'profile.html', profile)


def post_view(request, username, post_id):
    post = get_object_or_404(
        models.Post, pk=post_id, author__username=username
    )
    comments = post.comments.all()
    form = forms.CommentForm()
    post_view = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'post.html', post_view)


@login_required
def new_post(request):
    form = forms.PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('index')
    new_post = {
        'form': form
    }
    return render(request, 'postform.html', new_post)


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(
        models.Post, pk=post_id, author__username=username
    )
    if request.user != post.author:
        return redirect('post_view', username=username, post_id=post_id)
    form = forms.PostForm(
        request.POST or None, files=request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post_view', username=username, post_id=post_id)
    post_edit = {
        'form': form,
        'post': post,
    }
    return render(request, 'postform.html', post_edit)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(
        models.Post, pk=post_id, author__username=username
    )
    form = forms.CommentForm(request.POST or None)
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.post = post
        form.save()
    return redirect('post_view', username=username, post_id=post_id)


@login_required
def follow_index(request):
    follower = request.user
    post_list = models.Post.objects.filter(author__following__user=follower)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    follow_index = {
        'page': page,
    }
    return render(request, 'follow.html', follow_index)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(models.User, username=username)
    if author != request.user:
        models.Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    follower = request.user
    models.Follow.objects.filter(
        user=follower, author__username=username
    ).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception=None):
    context = {
        'path': request.path
    }
    return render(request, 'misc/404.html', context, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
