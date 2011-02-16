import redis

#@todo is it correct use class attr for redis link? (Mulitithreading safe?)
class RedisLink(object):
    redis = 0

    @classmethod
    def factory(cls, *args, **kwargs):
        if not cls.redis:
            cls.redis = redis.Redis(*args, **kwargs)

        return cls.redis

class AuthenticationMiddleware(object):
    def process_request(self, request):
        user_id = 0
        username = ''
        if 'auth' in request.COOKIES:
            r = RedisLink.factory()

            check_user_id = r.get('auth:%s' % request.COOKIES['auth'])
            correct_auth_secret = r.get('uid:%s:auth' % check_user_id)

            if correct_auth_secret == request.COOKIES['auth']:
                user_id = check_user_id
                username = r.get('uid:%s:username' % user_id)

        request.user = User(user_id, username)

        return None


class User(object):
    id = None
    username = ''

    def __init__(self, id, username):
        self.id = id
        self.username = username

    def is_authenticated(self):
        if self.id:
            return True
        else:
            return False
