import cgi
import os
import logging
import random
import datetime
from django.utils import simplejson

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

# Set to true if we want to have our webapp print stack traces, etc
_DEBUG = True

class MoodPair(db.Model):
  created = db.DateTimeProperty(auto_now_add=True)
  moods   = db.ListProperty(db.Key)

class Mood(db.Model):
	name = db.StringProperty(required=True)
	moodpair_id = db.ReferenceProperty(MoodPair, collection_name='moodpair_id')
	count = db.IntegerProperty(default=0)
	created = db.DateTimeProperty(auto_now_add=True)
  
class Stats(db.Model):
  mood_id = db.ReferenceProperty(Mood, collection_name='mood_id')
  date = db.DateProperty()
  count = db.IntegerProperty(default=0)

def getMoodsForPair(moodpair_id):
  moodpair = MoodPair.get(moodpair_id)
  moods    = Mood.get(moodpair.moods)
  return moods

# increment overall count on mood, and daily count on stats  
def increment_mood_count(mood_id):
  obj = Mood.get(mood_id)
  obj.count += 1
  key = obj.put()
  
  date = datetime.date.today()

  sObj = Stats.all()
  sObj.filter("mood_id =", key)
  sObj.filter("date =", date)
  stats = sObj.get()
  if not stats:
    stats = Stats(mood_id=key,
                 date=date,
                 count=1)
  else:
    stats.count += 1
  
  stats.put()

# see if mood exists in database
def moodExists(name):
  mObj = Mood.all()
  mObj.filter("name =", name)
  mood = mObj.get()
  if not (mood):
    return False
  else:
    return True


# Get stats for a given date.
def getStatsForDate(date):
  sObj = Stats.all()
  sObj.filter("date =", date)
  stats = sObj.get()

# Get stats for a given date.
def getTodaysStatsForMoodPair(moodpair_id):
  date = datetime.date.today()
  moods = getMoodsForPair(moodpair_id)
  counts = []
  statistics = {}
  #get counts from stats
  for mood in moods:
    sObj = Stats.all()
    sObj.filter("date =", date)
    sObj.filter("mood_id =", mood.key())
    stat = sObj.get()
    if stat:
      count = stat.count
    else:
      count = 0
      
    counts.append(count)
    statistics[mood.name] = count
  
  percentage = calc_percentage(statistics)
  return percentage

# Calculate percentage of two values respective to their own
# expects a dictionary with two keys with int values
# returns array containg both percentages.
def calc_percentage(inputs):
  thekeys = inputs.keys()
  thevalues = inputs.values()
  
  left = float(thevalues[0])
  right = float(thevalues[1])
  sums = float(left + right)
  percent = []
  percent.append(int(round((left / sums)*100)))
  percent.append(int(round((right / sums)*100)))

  d = dict(zip(thekeys, percent))
  
  return d

class Greeting(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)

class AdminPage(webapp.RequestHandler):
  def get(self):

    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'
      
      template_values = {
        'wuast': '',
        }

      path = os.path.join(os.path.dirname(__file__), 'admin.html')
      self.response.out.write(template.render(path, template_values))
            
class MoodList(webapp.RequestHandler):
  def get(self):
        
    limit = self.request.get('limit')
    # offset = self.request.get('limit')
    
    moodpairs = []
    count = 0
    moodpairs_query = MoodPair.all().order('-created')
    for moodpair in moodpairs_query:
      moodpairs.append([])
      myMoods = Mood.get(moodpair.moods)
      for mood in myMoods:
        moodpairs[count].append(mood)

      count += 1
    
    template_values = {
      'moodpairs': moodpairs,
    }
    path = os.path.join(os.path.dirname(__file__), '_listMoods.html')
    self.response.out.write(template.render(path, template_values))


class Vote(webapp.RequestHandler):
  def get(self):
    if self.request.get('moodId'):
      mood_id = self.request.get('moodId')
      mood_pair_id = self.request.get('moodPairId')

      increment_mood_count(mood_id)


      self.response.out.write(simplejson.dumps({'success':'true'}))

    else:
      logging.debug('Nothing to vote on. %s' % self.request.get('moodId'))
        
      path = os.path.join(os.path.dirname(__file__), 'error.html')
      self.response.out.write(template.render(path,''))


class MoodStats(webapp.RequestHandler):
  def get(self):
    mood_pair_id = self.request.get('moodPairId')
    
    stats = getTodaysStatsForMoodPair(mood_pair_id)

    logging.error("HERER %s" % stats)
    template_values = {
      'stats': stats,
    }
    path = os.path.join(os.path.dirname(__file__), '_moodStats.html')
    self.response.out.write(template.render(path, template_values))

class DisplayMoodPair(webapp.RequestHandler):
  def get(self):
    moodpairs = []
    count = 0
    moodpairs_query = MoodPair.all().order('-created')
    for moodpair in moodpairs_query:
      moodpairs.append([])
      myMoods = Mood.get(moodpair.moods)
      for mood in myMoods:
        moodpairs[count].append(mood)
        # logging.error('Pair ID. %s' % mood.moodpair_id.key)
        
      count += 1
 
 
    displayMoodPair = random.choice(moodpairs)
 
    counter = 0
    for mood in displayMoodPair:
      if (counter == 0):
        colorClass = 'green'
      else:
        colorClass = 'red'
      template_values = {
        'moodpair_id': mood.moodpair_id.key(),
        'mood_id': mood.key(),
        'mood_name': mood.name,
        'colorClass': colorClass,
      }
      path = os.path.join(os.path.dirname(__file__), '_showPair.html')
      render = template.render(path, template_values)
      self.response.out.write(render)
      counter += 1
    
    
class MainPage(webapp.RequestHandler):
  def get(self):
    
    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'url': url,
      'url_linktext': url_linktext,
      }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))


class MoodDelete(webapp.RequestHandler):
  def post(selt):
    errors = []
    

class MoodAdd(webapp.RequestHandler):
      def post(self):
        errors = []
        mood1 = self.request.get('mood1')
        mood2 = self.request.get('mood2')

        if(moodExists(mood1)):
          self.response.out.write( mood1+" already exists")
          return False
        if(moodExists(mood2)):
          self.response.out.write( mood2+" already exists")
          return False
          
        newMoodPair = MoodPair()
        mkey = newMoodPair.put()
        
        # logging.error('PAIR. %s' % newMoodPair.Key)
        m1 = Mood(name = mood1, moodpair_id=mkey)
        m2 = Mood(name = mood2, moodpair_id=mkey)

        newMoodPair.moods = [m1.put(), m2.put()]
        mkey = newMoodPair.put()
                
        template_values = {
          'errors': errors,
          }

class Guestbook(webapp.RequestHandler):
  def post(self):
    greeting = Greeting()

    if users.get_current_user():
      greeting.author = users.get_current_user()

    greeting.content = self.request.get('content')
    greeting.put()
    self.redirect('/')

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/displayMoodPair', DisplayMoodPair),
                                      ('/moodList', MoodList),
                                      ('/moodStats', MoodStats),
                                      ('/vote', Vote),
                                      ('/admini', AdminPage),
                                      ('/add', MoodAdd)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
