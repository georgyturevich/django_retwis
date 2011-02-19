from django.shortcuts import render_to_response
from django.template.context import RequestContext
from forms import RegisterForm, LoginForm, PostForm
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponseForbidden
from models import User, Post, logout as model_logout, get_user_posts, get_user_news

def logout(request):
    if request.user.is_authenticated():
        request.user.destroy_auth()

    return HttpResponseRedirect('/')

def profile(request, username):
    profile_user = User.fetch_one_by_username(username)
    if not profile_user.id:
        return HttpResponseNotFound('User with this username (%s) not found' % username)

    posts = get_user_posts(profile_user.id, 0, -1)

    can_follow = request.user.is_authenticated() and request.user.id != profile_user.id
    is_following = can_follow and request.user.is_following(profile_user.id)

    tpl_vars = {'profile_user': profile_user, 'posts': posts, 'can_follow': can_follow, 'is_following': is_following}
    return render_to_response('profile.html', tpl_vars, context_instance=RequestContext(request))

def follow(request, user_id, stop = None):
    if not request.user.is_authenticated():
        return HttpResponseForbidden('You must authorize!')

    follow_user = User.fetch_one(user_id)
    if not follow_user.id:
        return HttpResponseNotFound('User with this user id (%s) not found' % user_id)

    if stop == 'stop':
        request.user.stop_following(user_id)
    else:
        request.user.follow(user_id)

    return HttpResponseRedirect('/profile/%s/?success_follow=1' % follow_user.username)

def timeline(request):
    usernames = User.get_all_usernames()
    posts = Post.fetch_from_timeline(0, 50)
    tpl_vars = {'usernames': usernames, 'posts': posts}
    return render_to_response('timeline.html', tpl_vars, context_instance=RequestContext(request))

def index(request):

    #@todo How to set form data without calling constructor?
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

    if 'post' in request.POST:
        post_form = PostForm(request.POST)
        if post_form.is_valid():
            post_form.save(request)
            return HttpResponseRedirect('/?succes_post=1')
    else:
        post_form = PostForm()

    succes_register = 0
    if 'succes_register' in request.GET and request.GET['succes_register']:
        succes_register = 1

    posts = get_user_news(request.user.id, 0, -1)

    tpl_vars = {
        'register_form': register_form,
        'succes_register': succes_register,
        'login_form': login_form,
        'post_form': post_form,
        'posts': posts
    }
    return render_to_response('index.html', tpl_vars, context_instance=RequestContext(request))
