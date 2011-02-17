from hashlib import md5
from time import time
from models import RedisLink
from django import forms
from django.utils.translation import ugettext_lazy as _


#@todo Is it possible to set form action and submit in form class?
#@todo How to generate mulitple error messages for one field?
from retwis.models import User

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)
    password_again = forms.CharField(max_length=50, widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]

        r = RedisLink.factory()
        if r.get("username:%s:id" % username):
            message = _("A user with that username (%(username)s) already exists.") % {'username': username}
            raise forms.ValidationError(message)

        return username

    def clean_password_again(self):
        password = self.cleaned_data["password"]
        password_again = self.cleaned_data["password_again"]
        if password != password_again:
            raise forms.ValidationError(_("The two password fields didn't match."))

        return password_again

    def save(self):
        r = RedisLink.factory()

        username = self.cleaned_data["username"]
        password = self.cleaned_data["password"]

        user_id = r.incr("global:nextUserId")

        r.set("username:%s:id" % username, user_id)

        r.set("uid:%s:username" % user_id, username)
        r.set("uid:%s:password" % user_id, password)

#        authsecret = getrand()
#        r.set("uid:%s:auth" % user_id, authsecret)
#        r.set("auth:%s" % authsecret, user_id)

        # Manage a Set with all the users, may be userful in the future
        r.sadd("global:users", user_id)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)

    user_id = 0

    def clean_password(self):
        r = RedisLink.factory()

        username = self.cleaned_data["username"]
        password = self.cleaned_data["password"]

        user_id = r.get('username:%s:id' % username)
        correct_password = r.get('uid:%s:password' % user_id)
        if password != correct_password:
            raise forms.ValidationError(_("Password or user are incorrect"))

        self.user_id = user_id

        return password

    def login(self, response):
        r = RedisLink.factory()

        authsecret = getrand()
        r.set("uid:%s:auth" % self.user_id, authsecret)
        r.set("auth:%s" % authsecret, self.user_id)

        response.set_cookie('auth', authsecret, 3600)

        return None

class PostForm(forms.Form):
    status = forms.CharField(max_length=140, widget=forms.Textarea({'cols': 70, 'rows': 3}))

    def clean_status(self):
        status = self.cleaned_data['status']

        status = status.replace('\n'," ")
        status = status.replace('|'," ")

        return status

    def save(self, request):
        if not request.user.id:
            return

        r = RedisLink.factory()
        postid = r.incr("global:nextPostId")

        post_create_time = int(time())
        post = "%s|%s|%s" % (request.user.id , post_create_time, self.cleaned_data['status'])
        r.set('post:%s' % postid, post)

        r.lpush("uid:%s:posts" % request.user.id, postid)

        request.user.add_post_to_followers_news(postid, post_create_time)

def getrand():
    # @todo Use normal some rand() function :)
    fd = open("/dev/urandom")
    data = fd.read(16)
    fd.close()
    return md5(data).hexdigest()
