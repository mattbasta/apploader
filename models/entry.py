from google.appengine.ext import db


class Entry(db.Model):
    time = db.DateTimeProperty(required=True)
    url = db.StringProperty(required=True)
    slug = db.StringProperty(required=True)
    packaged = db.BooleanProperty(required=True)
