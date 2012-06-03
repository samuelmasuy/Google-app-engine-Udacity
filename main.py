import os
import re
import random
import hashlib
import hmac
import logging
import json
import time
import datetime
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import mail

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    pass

def make_secure_val(val):
    pass

def check_secure_val(secure_val):
    pass

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)

    def set_secure_cookie(self, name, val):
        pass

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'

class MainPage(BlogHandler):
  def get(self):
      self.write('Hello, Udacity!')
      self.write('<br><br><a href="/wiki/">Go To WikiPage!</a>')


##### user stuff
def make_salt(length = 5):
    pass

def make_pw_hash(name, pw, salt = None):
    pass

def valid_pw(name, password, h):
    pass

def users_key(group = 'default'):
    pass

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


##### blog stuff

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    content = db.TextProperty(required = True)
    path = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    user_post = db.StringProperty(required = True)

    def render(self):
        def replace_all(text, dic):
            for i, j in dic.iteritems():
                text = text.replace(i, j)
            return text
        reps = {'\n':'<br>', ' ':'&nbsp;', 'script':'skip', 'img':'gim', 'meta':'tema', 'head':'dead'}
        # self._render_text = replace_all(self.content, reps)
        self._render_text = self.content

        return render_str("post.html", p = self)

    def as_dict(self):
        time_fmt = '%c'
        d = {'content': self.content,
             'created': self.created.strftime(time_fmt),
             'last_modified': self.last_modified.strftime(time_fmt),
             'user_post': self.user_post}
        return d

def queryWiki(key):
    keyp = str(key)
    Timesp = "timep"+keyp
    post = memcache.get(keyp)

    if post is None: 
        logging.error(key)
        post = Post.get_by_id(key, parent = blog_key())
        logging.error("DB QUERY")
        logging.error(post)
        memcache.set(keyp, post)
        memcache.set(Timesp,(time.time()))
    query_time = time.time() - memcache.get(Timesp)
    query_time = int(query_time)
    return post, query_time

class WikiPage(BlogHandler):
    def get(self, post_id):

        u = Post.all().filter('path =', post_id).order('-created').get()
        if u is None:
            self.redirect('/wiki/_edit%s' % str(post_id))   
        else:
            key = u.key().id()
            version = self.request.get("v")
            if version:
                key = int(version)
            
            logging.error(key)
            post, query_time = queryWiki(key)
            if self.format == 'html':
                self.render("permalink.html", post = post, post_id=post_id, query_time = query_time)
            else:
                self.render_json(post.as_dict())

class Flush(BlogHandler):
    def get(self):
        memcache.flush_all()
        self.redirect('/')

class EditPage(BlogHandler):
    def get(self, post_id):
        if self.user:
            version = self.request.get("v")
            if version:
                key = int(version)
                post = Post.get_by_id(key, parent = blog_key())
            else:
                post = Post.all().filter('path =', post_id).order('-created').get()
            if post is not None:
                content = post.content
                self.render("editwiki.html", post_id=post_id, content=content)
            else:
                self.render("editwiki.html")
        else:
            self.redirect("/login")

    def post(self, post_id):
        if not self.user:
            self.redirect('/wiki')

        content = self.request.get('content')
        user_post = self.user.name
        key_name = post_id

        p = Post(parent = blog_key(), path=key_name, post_id=post_id, content = content, user_post = user_post)
        p.put()
        logging.error(str(p.last_modified))
        queryHistory(post_id, update = True)
        logging.error("yesy")
        self.redirect('/wiki%s?v=%s' % (str(post_id), str(p.key().id())))

def queryHistory(post_id, update = False):
    keyp = str(post_id)
    Timesp = "timep"+keyp
    post = memcache.get(keyp)
    logging.error(post_id)
    if not post or update: 
        post = db.GqlQuery("SELECT * FROM Post WHERE path= :1 ORDER BY created DESC", post_id)
        post = list(post)
        logging.error(post)
        memcache.set(keyp, post)
        memcache.set(Timesp,(time.time()))

    query_time = time.time() - memcache.get(Timesp)
    query_time = int(query_time)
    return post, query_time
    
class HistoryPage(BlogHandler):
    def get(self, post_id):
        u = Post.all().filter('path =', post_id).get()
        logging.error(u)
        if u is None:
            self.redirect('/wiki/_edit%s' % str(post_id))   
        else:
            post, query_time = queryHistory(post_id)
            if self.format == 'html':

                self.render('historywiki.html', post = post, post_id=post_id, query_time=query_time)
            else:
                self.render_json(post.as_dict())
        
USER_RE = re.compile(r"^[A-Za-z0-9'\.&@:?!()$#^]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^[A-Za-z0-9'\.&@:?!()$#^]{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

passwordkeysecret = 'somerandompassword'
class checkUsername(BlogHandler):
    def get(self):
        self.username = self.request.get('username')
        u = User.by_name(self.username)
        if u:
            # msg = 'That user already exists.'
            self.write('notgood')

class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "Not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "Not a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Passwords do not match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "Not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        pass
        # raise NotImplementedError

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            if self.email:
                message = mail.EmailMessage(sender="http://udacity-sam.appspot.com <x@gmail.com>",
                                subject="Your account has been approved")

                message.to = "%s <%s>"%(self.username, self.email)
                message.body = """
                Dear %s:

                Your account has been approved.  You can now visit
                http://udacity-sam.appspot.com and sign in using your Account to
                access the blog.

                Please let us know if you have any questions.

                The udacity-sam Team                """%(self.username)

                message.send()
            self.redirect('/welcome')

class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        remember = self.request.get('remember')

        u = User.login(username, password)
        if u:
            if remember:
                logging.error("hello")
                expire = (datetime.datetime.now() + datetime.timedelta(weeks=4)).strftime('%a, %d %b %Y %H:%M:%S GMT')
                cookie_val = make_secure_val(str(u.key().id()))
                self.response.headers.add_header('Set-Cookie', 'user_id=%s; path=/; expires="%s" ' %(cookie_val, expire))
            else:
                self.login(u)
            self.redirect('/welcome')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/wiki/')

class Welcome(BlogHandler):
    def get(self):
        if self.user:
            self.render('welcome.html', username = self.user.name)
        else:
            self.redirect('/signup')



PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'

app = webapp2.WSGIApplication([('/signup', Register),
                               ('/checkuser', checkUsername),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/wiki/_edit' + PAGE_RE, EditPage),
                               ('/wiki/_history' + PAGE_RE, HistoryPage),
                               ('/wiki' + PAGE_RE, WikiPage),
                               ('/', MainPage),
                               ('/welcome', Welcome),
                               ('/flush', Flush),
                               ],
                               debug=True)
