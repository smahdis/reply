# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.utils import timezone
from django import template
from homepage.models import Post, Vote
from django.utils.encoding import python_2_unicode_compatible, smart_unicode

from django.utils.timesince import timesince
import math
import logging
import sys
logger = logging.getLogger(__name__)
from django.db.models import Q, Sum
from khayyam import *
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

register = template.Library()

@register.filter
def trim_end(value):
    info = (value[:250] + '..') if len(value) > 250 else value
    return info

@register.filter
def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    time = timezone.localtime(time)
    time = time.replace(tzinfo=None)
    from datetime import datetime
    now = datetime.now()
    # now = timezone.localtime(timezone.now())

    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        # if second_diff < 10:
        #     return "همین الان"
        if second_diff < 60:
            return "همین الان"
        if second_diff < 120:
            return "یک دقیقه پیش"
        if second_diff < 3600:
            return str(second_diff / 60) + " دقیقه قبل"
        if second_diff < 7200:
            return "یک ساعت پیش"
        if second_diff < 86400:
            return str(second_diff / 3600) + " ساعت قبل"
    if day_diff == 1:
        return "دیروز"
    if day_diff < 7:
        return str(day_diff) + " روز قبل"
    if day_diff < 31:
        return str(day_diff / 7) + " هفته قبل"
    if day_diff < 365:
        return str(day_diff / 30) + " ماه قبل"
    return str(day_diff / 365) + " سال قبل"

colorList = ['#f16364','#f58559','#f9a43e','#215288','#67bf74','#59a2be',
             '#2093cd','#ad62a7','#00213B','#33777b','#006292','#0062E8',
             '#00A400','#00A47E','#3C0059','#701EB7','#B553B7','#E54363',
             '#4374E6','#093145','#0c374d','#0d3d56','#3c6478','#107896','#1496bb',]

@register.filter
def colorise(id):
    id = abs(hash(id)) % (10 ** 8)
    colorNum = abs(id%colorList.__len__())
    return colorList[colorNum]

@register.filter
def xstr(s):
    if s is None:
        return ''
    return str(s).encode('utf8')

@register.filter
def total_votes(var):
    post = var
    check_time = timezone.datetime.now() - timezone.timedelta(hours=24)
    dt_aware = timezone.make_aware(check_time, timezone.get_current_timezone())
    number_of_votes = Vote.objects.filter(post=post).filter(~Q(vote_type = 0)).aggregate(vote_num=Sum('vote_type'))

    return number_of_votes.get('vote_num')

@register.filter
def userVotedThisPost(var, uid):
    if uid is None:
        return False

    post = var
    user_id = uid

    check_time = timezone.datetime.now() - timezone.timedelta(hours=24)
    dt_aware = timezone.make_aware(check_time, timezone.get_current_timezone())
    v = Vote.objects.get(post=post, user_id = user_id, date_voted__gte = dt_aware)

    if v:
        return v.vote_type
    else:
        return False

@register.filter
def to_jalali(date):
    time = timezone.localtime(date)
    time = time.replace(tzinfo=None)
    # jalali = jdatetime.date.fromgregorian(date=time)
    jalali = JalaliDatetime(time).strftime('%A %d %B %y');
    return jalali

@register.filter
def getPostAnswersCount(post):
    answers = Post.objects.filter(is_question=0, is_published=1, question_id__exact=post.id).order_by('-created_date')
    return answers.count()

@register.filter
def get_parent_question(post):
    title=''
    try:
        title = Post.objects.get(is_question=1, is_published=1, id = post.question_id).post_title
    except Post.DoesNotExist:
        title='not exist'

    return title

@register.filter
def find_username(user):
    # username = ''

    if len(user.first_name) > 1:
        return user.first_name
    else:
        phone = user.username
        if(len(phone) < 13):
            phone = phone.lstrip('0')

        filtered_number = re.sub(r".*?(\d{3})(\d{4})(\d{3})", r'0\1####\3', phone)
        return filtered_number