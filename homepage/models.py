# from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.encoding import python_2_unicode_compatible
from taggit.managers import TaggableManager

@python_2_unicode_compatible
class Post(models.Model):
    poster = models.ForeignKey('auth.User')
    question = models.ForeignKey('self', null=True, blank=True)

    post_title = models.CharField(max_length=300)
    post_content = models.TextField(null=True, blank=True)

    votes = models.IntegerField(null=True, blank=True)
    views = models.IntegerField(null=True, blank=True)

    is_published = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    is_question = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)
    date_modified = models.DateTimeField(
            blank=True, null=True)

    tags = TaggableManager()




    def return_tags(self):
        taglist = self.tags.names()
        return taglist

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.post_title

@python_2_unicode_compatible
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=200, null=True, blank=True)
    profession = models.CharField(max_length=200, null=True, blank=True)
    degree = models.CharField(max_length=200, null=True, blank=True)
    status = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    # @classmethod
    # def create(cls, title):
    #     book = cls(title=title)
    #     # do something with the book
    #     return book
    def __str__(self):
        return self.user.username

class Authenticate(models.Model):
    mobile_number = models.CharField(max_length=20)
    authentication_id = models.CharField(max_length=20)
    created_date = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.mobile_number


@python_2_unicode_compatible
class Vote(models.Model):
    user = models.ForeignKey('auth.User')
    post = models.ForeignKey('Post')
    vote_type = models.SmallIntegerField()#NullBooleanField(null=True)
    date_voted = models.DateTimeField(
            default=timezone.now)
    def __str__(self):
        return self.user