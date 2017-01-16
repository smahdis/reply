# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.utils import timezone
from django import template
from django.utils.timesince import timesince
import math

register = template.Library()

# def lower(value): # Only one argument.
#     """Converts a string into all lowercase"""
#     return value.lower()
# @python_2_unicode_compatible
# @register.filter
# def days_ago(value):
#     # now = datetime.now()
#     now = timezone.now()
#     print (now, value)
#     try:
#         difference = now - value
#     except:
#         return value
#
#     if difference <= timedelta(minutes=1):
#         return 'just now'
#     return '%(time)s ago' % {'time': timesince(value)}#.split(', ')[0]}

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

colorList = ['#f16364','#f58559','#f9a43e','#e4c62e','#67bf74','#59a2be',
             '#2093cd','#ad62a7','#00213B','#00623B','#006292','#0062E8',
             '#00A400','#00A47E','#3C0059','#701EB7','#B553B7','#E54363',
             '#4374E6','#093145','#0c374d','#0d3d56','#3c6478','#107896','#1496bb',]

@register.filter
def colorise(id):
    colorNum = abs(id%colorList.__len__())
    return colorList[colorNum]