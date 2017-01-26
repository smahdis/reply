from django.shortcuts import render
from django.utils import timezone
from .models import Post, Authenticate
from django.shortcuts import render, get_object_or_404
from .forms import PostForm, RegisterNewUser
from django.shortcuts import redirect
import logging
from django.http import JsonResponse
from django.contrib.auth.models import User
import re
import sys
import logging
import pytz
logger = logging.getLogger(__name__)
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

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

def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    form = RegisterNewUser()
    return render(request, 'registration/register.html', {'form': form})

def validate_username(request):
    number = request.GET.get('phone', None)
    rule = re.compile(r'^(?:\+?98)?[(09)]\d{9,13}$')
    matched = rule.search(number)
    authentication_id = User.objects.make_random_password(length=6, allowed_chars='0123456789')
    if matched:
        authenticate, created = Authenticate.objects.update_or_create(mobile_number=number, defaults={"mobile_number": number, "authentication_id": authentication_id, "created_date": timezone.now()})
        matched = True
    else:
        matched = False
    logger.debug("this is a debug message!")

    data = {
        'matched': matched,#User.objects.filter(username__iexact=username).exists()
        'number': number,
        'authentication_id': authentication_id,
    }
    return JsonResponse(data)


def validate_phone_number(request):
    phone_number = request.GET.get('phone_number', None)
    auth_id = request.GET.get('auth_id', None)
    check_time = timezone.datetime.now() - timezone.timedelta(minutes=30)
    dt_aware = timezone.make_aware(check_time, timezone.get_current_timezone())
    result = Authenticate.objects.filter(mobile_number=phone_number, authentication_id=auth_id, created_date__gte=dt_aware)

    # logger.error('Something went wrong!')
    # print >> sys.stderr, 'Goodbye, cruel world!'

    logged_in = False

    if result.exists():
        if not User.objects.filter(username=phone_number).exists():
            result.delete()
            password = User.objects.make_random_password(length=12,allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            user = User.objects.create_user(phone_number, password=password)
            if user is not None:
                logger.error('User registered and logged in')
                logged_in = True
                login(request, user)
        else:
            user = authenticate(username=phone_number)
            if user is not None:
                if user.is_active:
                    logged_in = True
                    login(request, user)

    data = {
        'verified': result.exists(),
        'logged_in': logged_in,
        'redirect': '../'
    }
    return JsonResponse(data)

def logout_view(request):
    logout(request)
    request.session.flush()
    # request.user = AnonymousUser
    # Redirect to a success page.
    return redirect('index')
    # return HttpResponseRedirect(request,'/')


@login_required
def dashboard(request):
    return render(request, 'homepage/dashboard.html')