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

import json
import markdown
from datetime import datetime
from google.appengine.api import urlfetch
from google.appengine.api import memcache
import urllib
from models import Post

from flask import Flask, request, jsonify, make_response, render_template

app = Flask(__name__)
app.config["SITE_NAME"] = u"SITE_NAME"
app.config["AUTHOR"] = u"AUTHOR"
app.config["domain"] = ".DOMAIN"
app.debug = True

API_URL = "https://fornsigtuna.appspot.com/api"

app.config["Language_list"] = [
    ("zh-tw", u"正體中文（台湾）"),
    ("zh-hk", u"繁體中文（香港、澳门）"),
    ("zh-cn", u"简体中文（中国大陆）"),
]

LANG_LIST = ["zh-tw", "zh-hk", "zh-cn", "zh-hans", "zh-hant"]


@app.template_filter('md')
def md_full_filter(text):
    return markdown.markdown(text, extensions=[
        "markdown.extensions.extra",
        "markdown.extensions.toc",
        "markdown.extensions.nl2br"
    ])


@app.context_processor
def inject():
    return {'now': datetime.utcnow(), 'locale': request.headers.get('Accept-Language', "en").split(",")[0]}


@app.errorhandler(404)
def page_not_found(e):
    return "Error : 404 - Page Not Found", 404


def zh_conv(text, target_lang):
    form_data = urllib.urlencode({"text": text, "lang": target_lang})
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    result = urlfetch.fetch(
        url='https://zh-conv.liantian.me/api',
        # url=API_URL,
        payload=form_data,
        method=urlfetch.POST,
        headers=headers)
    data = json.loads(result.content, encoding="utf-8")
    return data[u'result']


@app.route('/')
def index():
    post = Post.query().get()

    acc_lang = request.headers.get('Accept-Language', "en").split(",")[0]
    sub_domain = request.headers['Host'].split(".")[0]
    if sub_domain == "default":
        text = post.text
    elif sub_domain in LANG_LIST:
        text = memcache.get(sub_domain)
        if text is None:
            text = zh_conv(post.text, sub_domain)
            memcache.add(key=sub_domain, value=text, time=86400)
    else:
        text = post.text

    return render_template("index.html", text=text)
