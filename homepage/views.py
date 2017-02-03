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
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import constants
from homepage.templatetags import my_tags

def index(request):
    posts = Post.objects.filter(created_date__lte=timezone.now(), is_question=1, is_published=1).order_by('-created_date')
    paginator = Paginator(posts, constants.QUESTIONS_PER_PAGE)
    page = request.GET.get('page')
    try:
        paged_posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paged_posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paged_posts = paginator.page(paginator.num_pages)
    return render(request, 'homepage/index.html', {'posts': paged_posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, is_question=1)
    answers = Post.objects.filter(is_question=0, question_id__exact=pk, is_published=1).order_by('created_date')
    paginator = Paginator(answers, constants.ANSWERS_PER_PAGE)
    page = request.GET.get('page')
    try:
        paged_answers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paged_answers = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paged_answers = paginator.page(paginator.num_pages)
    return render(request, 'homepage/posts/post_detail.html', {'post': post, 'answers': paged_answers})

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

@login_required()
def edit_answer(request):
    pk = request.GET.get('pk', None)
    content = request.GET.get('content', None)
    post = Post.objects.get(pk=pk)

    new_post_pk = -1
    if request.user.is_authenticated and post and request.user.is_active and request.user == post.poster:
        post.post_content = content
        post.save()
        success = True
        data = {
            'success': success,
            'pk': pk,
            'redirect': '../../../question/' + str(post.question_id),
        }
    else:
        success = False
        data = {
            'success': False,
        }
    return JsonResponse(data)


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

from django.contrib.auth.models import Permission

@login_required
def dashboard(request):
    print >> sys.stderr, Permission.objects.all()
    print >> sys.stderr, request.user.has_perm('can_change_post')
    posts = Post.objects.filter(created_date__lte=timezone.now(), is_question=1, is_published=1, poster=request.user).order_by('-created_date')[:10]
    answers = Post.objects.filter(is_question=0, is_published=1, poster=request.user).order_by('-created_date')[:10]
    votes = Vote.objects.filter(post__poster=request.user).filter(~Q(vote_type = 0)).aggregate(vote_num=Coalesce(Sum('vote_type'),0))

    return render(request, 'homepage/dashboard.html', {'posts': posts, 'answers': answers, 'votes': votes.get('vote_num')})


@login_required()
def vote(request):
    check_time = timezone.datetime.now() - timezone.timedelta(hours=24)
    dt_aware = timezone.make_aware(check_time, timezone.get_current_timezone())
    pk = request.GET.get('pk', None)
    vt = request.GET.get('vote_type', None)
    post = get_object_or_404(Post, pk=pk)
    number_of_votes = 0
    if request.user.is_authenticated:
        error = False
        if not post.poster==request.user:
            try:
                v = Vote.objects.get(user=request.user, post=post,date_voted__gte = dt_aware)
                if v:
                    if v.vote_type == int(vt):
                        vt=0
            except Vote.DoesNotExist:
                print >> sys.stderr, "vote didn't exist previously"

            vote_date = timezone.now()
            vote, created = Vote.objects.update_or_create(user=request.user, post=post,date_voted__gte = dt_aware, defaults={'date_voted': vote_date, 'vote_type':vt})
            if(vt==0):
                vote.delete();

            votes = Vote.objects.filter(post=post).filter(~Q(vote_type = 0)).aggregate(vote_num=Coalesce(Sum('vote_type'),0))
            number_of_votes =  votes.get('vote_num')
            self_voting = False
        else:
            self_voting = True
    else:
        error=True

    data = {
        'number_of_votes': number_of_votes,
        'vt': int(vt),
        'error':error,
        'self_voting': self_voting
    }
    return JsonResponse(data)


@login_required()
def set_profile(request):
    name = request.GET.get('name', None)
    city = request.GET.get('city', None)
    user = User.objects.get(username=request.user.username)
    if not request.user.is_authenticated and len(name) < 5 :
        success = False
    else:
        user.first_name=name;
        user.save();
        success = True

    user.last_name = city;
    data = {
        'success': success,
        'name': name
    }
    return JsonResponse(data)

@login_required()
def answer_question(request):
    pk = request.GET.get('pk', None)
    content = request.GET.get('content', None)
    post = Post.objects.get(pk=pk)
    post = Post.objects.create(poster=request.user, is_question=0, question_id=pk, post_title = post.post_title, post_content = content, published_date = timezone.now(), tags=None,)
    new_post_pk = -1

    if request.user.is_authenticated and post:
        success = True
        new_post_pk = post.pk
        color = my_tags.colorise(post.pk);
        data = {
            'success': success,
            'pk': new_post_pk,
            'redirect': '../',
            'color': color
        }
    else:
        success = False
        data = {
            'success': False,
        }


    return JsonResponse(data)