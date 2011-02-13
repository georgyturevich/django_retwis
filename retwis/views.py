from django.shortcuts import render_to_response

import redis

def index(request):
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
    return render_to_response('index.html', tpl_vars)
