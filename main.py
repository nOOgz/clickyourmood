import cgi
import os
import logging
import random
import datetime

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

# Set to true if we want to have our webapp print stack traces, etc
_DEBUG = True

class Mood(db.Model):
	name = db.StringProperty(required=True)
	count = db.IntegerProperty(default=0)
	created = db.DateTimeProperty(auto_now_add=True)

class MoodPair(db.Model):
  created = db.DateTimeProperty(auto_now_add=True)
  moods   = db.ListProperty(db.Key)
  
class Stats(db.Model):
  mood_id = db.StringProperty(db.Key)
  date = db.DateProperty()
  count = db.IntegerProperty(default=0)

# increment overall count on mood, and daily count on stats  
def increment_mood_count(mood_id):
  obj = Mood.get(mood_id)
  obj.count += 1
  obj.put()
  
  date = datetime.date.today()

  sObj = Stats.all()
  sObj.filter("mood_id =", mood_id)
  sObj.filter("date =", date)
  stats = sObj.get()
  if not stats:
    stats = Stats(mood_id=mood_id,
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

# Calculate percentage of two values respective to their own
# returns array containg both percentages.
def calc_percentage(left, right):
  percent = []
  percent.append((1.0*(left + right)/left)*100)
  percent.append((1.0*(left + right)/right)*100)
  return percent


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
      self.response.out.write("success")
    else:
      logging.debug('Nothing to vote on. %s' % self.request.get('moodId'))
        
      path = os.path.join(os.path.dirname(__file__), 'error.html')
      self.response.out.write(template.render(path,''))


class MainPage(webapp.RequestHandler):
  def get(self):
    moodpairs = []
    count = 0
    moodpairs_query = MoodPair.all().order('-created')
    for moodpair in moodpairs_query:
      moodpairs.append([])
      myMoods = Mood.get(moodpair.moods)
      for mood in myMoods:
        moodpairs[count].append(mood)
      count += 1


    displayMoodPair = random.choice(moodpairs)
      
    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'displayMoodPair': displayMoodPair,
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
          errors.append( mood1+" already exists")
          return False
        if(moodExists(mood2)):
          errors.append( mood2+" already exists")
          return False
          
        newMoodPair = MoodPair()
        m1 = Mood(name = mood1)
        m2 = Mood(name = mood2)

        newMoodPair.moods = [m1.put(), m2.put()]
        newMoodPair.put()
        
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
                                      ('/moodList', MoodList),
                                      ('/vote', Vote),
                                      ('/admini', AdminPage),
                                      ('/add', MoodAdd)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
