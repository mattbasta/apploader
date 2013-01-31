#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import datetime
import json
import random
import urllib
from StringIO import StringIO
from zipfile import ZipFile, ZIP_DEFLATED

import webapp2
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from webapp2_extras import jinja2

from models.entry import Entry


chars = "123456789abcdef"


def nice_guid():
    return "".join([random.choice(chars) for _ in range(5)])


class BaseHandler(webapp2.RequestHandler):
    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_template(self, template, **context):
        rv = self.jinja2.render_template(template, **context)
        self.response.write(rv)


class BaseUploadHandler(blobstore_handlers.BlobstoreUploadHandler,
                        BaseHandler):
    pass


class MainHandler(BaseHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload')
        self.render_template("homepage.html", upload_url=upload_url)

    def post(self):
        url = self.request.get("url", "")
        if url:
            slug = nice_guid()
            entry = Entry(time=datetime.datetime.now(),
                          url=url, slug=slug, packaged=False)
            entry.put()
            self.render_template("code.html", slug=slug)
        else:
            return self.get()


class UploadHandler(BaseUploadHandler):
    def post(self):
        upload_files = self.get_uploads('package')
        blob_info = upload_files[0]

        slug = nice_guid()
        entry = Entry(time=datetime.datetime.now(),
                      url=str(blob_info.key()), slug=slug, packaged=True)
        entry.put()

        self.render_template("code.html", slug=slug)


class GetHandler(BaseHandler):
    def get(self, slug):
        app = Entry.all().filter('slug =', slug).get()
        if app.packaged:
            self.render_template("install.html", url='/minifest/%s' % slug,
                                 packaged=True)
        else:
            self.render_template("install.html", url=app.url, packaged=False)


class MinifestHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, slug):
        self.response.headers.add_header(
            "Content-type", "application/x-web-app-manifest+json")

        try:
            app = Entry.all().filter('slug =', slug).get()
        except Exception:
            self.response.write('{"error":"Not found."}')
            return

        try:
            blob_reader = blobstore.BlobReader(app.url)
        except Exception:
            self.response.write('{"error":"Could not retrieve package."}')
            return

        try:
            package = ZipFile(StringIO(blob_reader.read()))
        except Exception:
            self.response.write('{"error":"Could not retrieve package."}')
            return

        try:
            manifest = package.read("manifest.webapp")
        except Exception:
            self.response.write('{"error":"Could not open manifest."}')
            return

        try:
            unjsoned = json.loads(manifest)
        except Exception:
            self.response.write('{"error":"Could not parse manifest."}')
            return

        try:
            name = unjsoned["name"]
        except Exception:
            self.response.write('{"error":"Could not read app name."}')
            return

        try:
            version = unjsoned["version"]
        except Exception:
            self.response.write('{"error":"Could not read app version."}')
            return

        self.response.write(json.dumps({
            "name": name,
            "package_path": "/serve/%s" % app.url,
            "version": version,
        }))


class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        self.send_blob(blobstore.BlobInfo.get(resource))


app = webapp2.WSGIApplication([
    ('/upload', UploadHandler),
    ('/minifest/(.+)', MinifestHandler),
    ('/serve/(.+)', ServeHandler),
    ('/([%s]+)' % chars, GetHandler),
    ('/', MainHandler),
], debug=True)
