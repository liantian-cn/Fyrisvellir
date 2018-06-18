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

import io
import json
import urllib
from datetime import datetime
import base62

from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext import ndb

import markdown
from flask import Flask, request, render_template, redirect, send_file
from models import Post, Attachment

app = Flask(__name__)
app.debug = False

ZH_CONV_API_URL = "https://fornsigtuna.appspot.com/api"

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
    form_data = urllib.urlencode({"text": text.encode("utf-8"), "lang": target_lang})
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    result = urlfetch.fetch(
        url=ZH_CONV_API_URL,
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
    if sub_domain in LANG_LIST:
        text = memcache.get(sub_domain)
        if text is None:
            text = zh_conv(post.text, sub_domain)
            memcache.add(key=sub_domain, value=text, time=3600)
    else:
        if acc_lang in LANG_LIST:
            return redirect("{0}://{1}{2}".format(request.scheme, acc_lang, post.domain), code=302)
        text = post.text
    return render_template("index.html", text=text, post=post)


@app.route('/att/<key>/<filename>', methods=['GET'])
def download(key, filename):
    if request.if_modified_since:
        return "HTTP_304_NOT_MODIFIED", 304
    memcache_key = 'download_{}'.format(key)
    data = memcache.get(memcache_key)
    if data is None:
        int_key = base62.decode(key)
        doc = ndb.Key(Attachment, int_key).get()
        data = send_file(io.BytesIO(doc.file),
                         mimetype=doc.mime_type,
                         as_attachment=True,
                         attachment_filename=doc.filename.encode('utf-8'),
                         add_etags=True,
                         cache_timeout=86400 * 365,
                         conditional=True,
                         last_modified=doc.created)
        memcache.add(memcache_key, data, 86400 * 30)
    return data
