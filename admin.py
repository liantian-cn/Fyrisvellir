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

import mimetypes
import random
import string
import base62

# from google.appengine.api import images
from google.appengine.runtime.apiproxy_errors import RequestTooLargeError

from flask import Flask, request, jsonify, render_template, url_for
from flask_bootstrap import Bootstrap
from forms import PostForm
from models import Post, Attachment

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = ''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(32))
Bootstrap(app)


@app.route('/admin/', methods=['POST', "GET"])
def index():
    post = Post.query().get()
    form = PostForm(obj=post)
    if form.validate_on_submit():
        form.save()
    return render_template("admin.html", post=post, form=form)


@app.route('/admin/editormd_image_upload/', methods=['POST'], endpoint="admin.editormd_image_upload")
def editormd_image_upload():
    mimetypes.init()
    if 'editormd-image-file' not in request.files:
        return jsonify({"success": 0, "message": u"No file part"})
    file = request.files['editormd-image-file']
    if file.filename == '':
        return jsonify({"success": 0, "message": u"No selected file"})
    if file:
        filename = file.filename
        mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        att = Attachment()
        att.filename = filename
        att.mime_type = mime_type
        f = file.read()
        if mime_type in ('image/jpeg', 'image/png', 'image/gif'):
            # f = images.im_feeling_lucky(f)
            pass
        att.file = f

        try:
            att_key = att.put()
        except RequestTooLargeError:
            return jsonify({"success": 0, "message": u"RequestTooLargeError"})
        url = url_for("download", key=base62.encode(att_key.integer_id()), filename=filename)
        return jsonify({"success": 1, "message": u"No allowed_file", "url": url})

    return jsonify({"success": 0, "message": u"No allowed_file"})


@app.route('/att/<key>/<filename>', methods=['GET'], endpoint="download")
def download(key, filename):
    return "None"
