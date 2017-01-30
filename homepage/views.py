from django.shortcuts import render
from django.utils import timezone
from .models import Post, Authenticate, Vote
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
from django.db.models import Q, Sum

def index(request):
    posts = Post.objects.filter(created_date__lte=timezone.now(), is_question=1, is_published=1).order_by('-created_date')
    return render(request, 'homepage/index.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    answers = Post.objects.filter(is_question=0, question_id__exact=pk, is_published=1).order_by('-created_date')
    return render(request, 'homepage/posts/post_detail.html', {'post': post, 'answers': answers})
@login_required()
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.poster = request.user
            # post.tags = request.tags
            post.published_date = timezone.now()
            post.save()
            # Without this next line the tags won't be saved.
            form.save_m2m()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'homepage/post_edit.html', {'form': form})

@login_required()
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.poster = request.user
            post.date_modified = timezone.now()
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
    matched = False
    if not request.user.is_authenticated:
        number = request.GET.get('phone', None)
        rule = re.compile(r'^(?:\+?98)?[(09)]\d{9,13}$')
        matched = rule.search(number)
        authentication_id = User.objects.make_random_password(length=6, allowed_chars='0123456789')

        # if not matched, django returns none, so we change it to false
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
    logged_in = False
    if not request.user.is_authenticated:
        phone_number = request.GET.get('phone_number', None)
        auth_id = request.GET.get('auth_id', None)
        check_time = timezone.datetime.now() - timezone.timedelta(minutes=30)
        dt_aware = timezone.make_aware(check_time, timezone.get_current_timezone())
        result = Authenticate.objects.filter(mobile_number=phone_number, authentication_id=auth_id, created_date__gte=dt_aware)

        # logger.error(result.exists())
        # print >> sys.stderr, 'Goodbye, cruel world!'


        if result.exists():


            if not User.objects.filter(username=phone_number).exists():
                # result.delete()

                password = User.objects.make_random_password(length=12,allowed_chars='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                print >> sys.stderr, password
                logger.error('error happenend here')
                logger.error(password)
                user = User.objects.create_user(phone_number, password=password)
                if user is not None:
                    logger.error('User registered and logged in')
                    logged_in = True
                    login(request, user)
            else:
                print >> sys.stderr, 'user exist'
                logger.error('user exist')
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


@login_required()
def upvote(request):
    check_time = timezone.datetime.now() - timezone.timedelta(hours=24)
    dt_aware = timezone.make_aware(check_time, timezone.get_current_timezone())
    pk = request.GET.get('pk', None)
    vt =  request.GET.get('vote_type', None)
    post = get_object_or_404(Post, pk=pk)
    try:
        v = Vote.objects.get(user=request.user, post=post,date_voted__gte = dt_aware)
        if v:
            if v.vote_type == int(vt):
                vt=0
    except Vote.DoesNotExist:
        print >> sys.stderr, "vote didn't exist previously"
            
    vote_date = timezone.now()
    vote, created = Vote.objects.update_or_create(user=request.user, post=post,date_voted__gte = dt_aware, defaults={'date_voted': vote_date, 'vote_type':vt})
    number_of_votes = Vote.objects.filter(post=post).filter(~Q(vote_type = 0)).aggregate(vote_num=Sum('vote_type'))
    # print >> sys.stderr, number_of_votes
    # print >> sys.stderr, number_of_votes.get('vote_num')
    print >> sys.stderr, request.is_tablet
    print >> sys.stderr, request.is_phone
    print >> sys.stderr, request.is_mobile
    data = {
        'number_of_votes': number_of_votes.get('vote_num'),
    }
    return JsonResponse(data)