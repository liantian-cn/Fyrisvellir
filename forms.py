#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# __author__ = 'Liantian'
# __email__ = "liantian.me+code@gmail.com"
#
# MIT License
#
# Copyright (c) 2018 liantian
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import datetime, date

from flask import request
from flask_wtf.form import FlaskForm
from google.appengine.ext import ndb

from wtforms.fields import StringField, SelectField, TextAreaField, BooleanField, SubmitField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import DataRequired, Regexp
from wtforms.widgets import TextInput, CheckboxInput
from wtforms.widgets.html5 import NumberInput

from main import app

from models import Post


class PostForm(FlaskForm, object):
    text = TextAreaField(label=u"内容文字", validators=[DataRequired()], description=u"使用兼容于Github的Markdown語法。")
    submit = SubmitField(label=u"修改")

    def __init__(self, obj=None, **kwargs):
        super(PostForm, self).__init__(obj=obj, **kwargs)
        self.obj = obj

    def save(self):
        if self.obj is None:
            post = Post()
        else:
            post = self.obj
        post.text = self.text.data
        post.put()
