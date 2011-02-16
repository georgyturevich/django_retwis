from django.shortcuts import render_to_response
from django.utils.translation import ugettext
from django.contrib import messages
from forms import RegisterForm
import redis
from django.http import HttpResponseRedirect

def timeline(request):
    r = redis.Redis()
    usernames = r.sort('global:users', get='uid:*:username', desc=True, start=0, num=10)
    posts_ids = r.lrange('global:timeline', 0, 50)

    posts = []
    for post_id in posts_ids:
        post_str = r.get('post:%s' % post_id)
        (user_id, create_time, message) = post_str.split('|')

        username = r.get('uid:%s:username' % user_id)

        posts.append({
            'username': username,
            'message': message
        })

    tpl_vars = {'usernames': usernames, 'posts': posts}
    return render_to_response('timeline.html', tpl_vars)

def index(request):
    if 'username' in request.POST:
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            return HttpResponseRedirect('/?succes_register=1')
    else:
        register_form = RegisterForm()

    succes_register = 0
    if 'succes_register' in request.GET and request.GET['succes_register']:
        succes_register = 1

    tpl_vars = {'register_form': register_form, 'succes_register': succes_register}

    return render_to_response('index.html', tpl_vars)
