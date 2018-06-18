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

from flask_wtf.form import FlaskForm
from models import Post
from wtforms.fields import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Regexp, Length


class PostForm(FlaskForm, object):
    text = TextAreaField(label=u"内容文字", validators=[DataRequired()], description=u"使用兼容于Github的Markdown語法。")
    site_name = StringField(label=u"站點名稱", validators=[DataRequired(), Length(max=20)])
    author = StringField(label=u"作者", validators=[DataRequired(), Length(max=20)])
    domain = StringField(label=u"根域名", validators=[Regexp(r'^[a-zA-Z\d-]{,63}(\.[a-zA-Z\d-]{,63})*$')])
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
        post.site_name = self.site_name.data
        post.author = self.author.data
        post.domain = self.domain.data.encode("utf-8")
        post.put()
