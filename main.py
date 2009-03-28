import cgi
import os

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
	count = db.IntegerProperty(default=0)
	created = db.DateTimeProperty(auto_now_add=True)



class Greeting(db.Model):
  author = db.UserProperty()
  content = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
  def get(self):
    moodpairs = []
    moodpairs_query = MoodPair.all().order('-created')
    for item in moodpairs_query:
      moodpairs.append(item)
    

    # 
    # myMoods = Mood.get(newMoodPair.moods)
    # moods = []
    # for mood in myMoods:
    #     moods.append([])
        # moods[newMoodPair.id].append(mood.name)
    
    
    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Logout'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Login'

    template_values = {
      'moodpairs': moodpairs,
      'url': url,
      'url_linktext': url_linktext,
      }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))


class MoodAdd(webapp.RequestHandler):
      def post(self):

        # if users.get_current_user():
        #   greeting.author = users.get_current_user()
        # 

        newMoodPair = MoodPair()
        m1 = Mood(name=self.request.get('mood1'))
        m2 = Mood(name=self.request.get('mood2'))

        newMoodPair.moods = [m1.put(), m2.put()]
        newMoodPair.put()
        
        self.redirect('/')



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
                                      ('/add', MoodAdd)],
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
