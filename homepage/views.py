from django.shortcuts import render
from django.utils import timezone
from .models import Post, Profile
from django.shortcuts import render, get_object_or_404
from .forms import PostForm
from django.shortcuts import redirect
import logging
from django.http import Http404

logger = logging.getLogger(__name__)

def index(request):
    posts = Post.objects.filter(created_date__lte=timezone.now(), is_question=1, is_published=1).order_by('-created_date')
    return render(request, 'homepage/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    answers = Post.objects.filter(is_question=0, question_id__exact=pk, is_published=1).order_by('-created_date')
    return render(request, 'homepage/post_detail.html', {'post': post, 'answers': answers})

def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.poster = request.user
            post.published_date = timezone.now()
            post.save()
            # Without this next line the tags won't be saved.
            form.save_m2m()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'homepage/post_edit.html', {'form': form})

def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.poster = request.user
            post.published_date = timezone.now()
            post.save()
            # Without this next line the tags won't be saved.
            form.save_m2m()
            return redirect('post_detail', pk=post.pk)
        # else:
        #     raise Http404
    else:
        form = PostForm(instance=post)
    return render(request, 'homepage/post_edit.html', {'form': form, 'post':post})