# -*- coding: utf-8 -*-
from django import forms

from .models import Post
from django.core.exceptions import ValidationError
import bleach
from django.conf import settings

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('post_title', 'post_content','tags')


        exclude = ('poster',)
        error_messages = {
            'post_title': {
                'max_length': "لطفا عنوان کوتاه تری انتخاب نمایید",
                'required':"لطفا عنوان را وارد نمایید",
            },
            'tags': {
                'max_length': "لطفا تگ کوتاه تری انتخاب نمایید",
                'required': "لطفا حداقل یک تگ (برچسب) وارد نمایید",
            },
        }



    def clean_tags(self):
        data = self.cleaned_data['tags']
        #Check date is not in past.
        if data.__len__() < 1:
            raise ValidationError('لطفا حداقل یک تگ وارد کنید.')
        # Remember to always return the cleaned data.
        return data

    def clean_post_content(self):
        data = self.cleaned_data['post_content']
        # myfield = self.cleaned_data.get('myfield', '')
        cleaned_text = bleach.clean(data,
                                    settings.BLEACH_VALID_TAGS,
                                    settings.BLEACH_VALID_ATTRS,
                                    settings.BLEACH_VALID_STYLES)
        return cleaned_text #sanitize html