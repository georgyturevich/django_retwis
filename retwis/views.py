from django.shortcuts import render_to_response
from django.template.context import Context, RequestContext, get_standard_processors
from forms import RegisterForm, LoginForm
from django.http import HttpResponseRedirect
from retwis.models import RedisLink
from models import logout as model_logout

def logout(request):
    model_logout(request)
    return HttpResponseRedirect('/')

def timeline(request):
    r = RedisLink.factory()

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
    return render_to_response('timeline.html', tpl_vars, context_instance=RequestContext(request))

def index(request):
    if 'create' in request.POST:
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            return HttpResponseRedirect('/?succes_register=1')
    else:
        register_form = RegisterForm()

    if 'login' in request.POST:
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            response = HttpResponseRedirect('/?succes_login=1')
            login_form.login(response)

            return response
    else:
        login_form = LoginForm()

    succes_register = 0
    if 'succes_register' in request.GET and request.GET['succes_register']:
        succes_register = 1

    tpl_vars = {'register_form': register_form, 'succes_register': succes_register, 'login_form': login_form}
    return render_to_response('index.html', tpl_vars, context_instance=RequestContext(request))
