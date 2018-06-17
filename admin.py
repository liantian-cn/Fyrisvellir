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

import os
import random
import string
import mimetypes
import os
import urllib
from datetime import datetime

import cloudstorage
from flask import flash
from flask import render_template, request, redirect, url_for, jsonify
from google.appengine.api import app_identity
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.datastore.datastore_query import Cursor
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from slugify import slugify

from forms import PostForm
from models import Post

from flask import Flask, request, jsonify, make_response, render_template
from flask_bootstrap import Bootstrap

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
        directory = "upload/{0}".format(datetime.now().strftime("%Y%m%d/%H"))
        bucket_name = os.environ.get(
            'BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
        bucket = '/' + bucket_name
        filename = "{0}/{3}/{1}.{2}".format(bucket, slugify(file.filename.rsplit('.', 1)[0]).replace("-", "_"), file.filename.rsplit('.', 1)[1], directory)
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
        gcs_file = cloudstorage.open(filename,
                                     'w',
                                     content_type=content_type,
                                     options={'x-goog-acl': 'public-read'},
                                     retry_params=write_retry_params)
        gcs_file.write(file.read())
        gcs_file.close()
        gs = "/gs{0}".format(filename)
        blob_key = blobstore.create_gs_key(gs)
        url = images.get_serving_url(blob_key, size=app.config["SITE_POST_IMG_WIDTH"], crop=False, secure_url=True)
        return jsonify({"success": 1, "message": u"No allowed_file", "url": url})

    return jsonify({"success": 0, "message": u"No allowed_file"})
