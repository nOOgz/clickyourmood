"""Model classes and utility functions for handling
Quotes, Votes and Voters in the Overheard application.

"""


import datetime
import hashlib

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users



class MoodPairs(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
	moods   = db.ListProperty(db.Key)


class Moods(db.Model):
	name = db.StringProperty(required=true)
	count = db.IntegerProperty(default=0)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    mood_pair = db.Reference(MoodPair)

