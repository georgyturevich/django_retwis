from django.utils.datetime_safe import datetime
from time import time
import redis
from hashlib import md5

#@todo is it correct use class attr for redis link? (Mulitithreading safe?)
class RedisLink(object):
    redis = 0

    @classmethod
    def factory(cls, *args, **kwargs):
        if not cls.redis:
            cls.redis = redis.Redis(*args, **kwargs)

        return cls.redis

class User(object):
    id = None
    username = ''

    def __init__(self, id, username):
        self.id = int(id)
        self.username = username

    def is_authenticated(self):
        if self.id:
            return True
        else:
            return False

    def is_following(self, check_user_id):
        r = RedisLink.factory()

        if r.sismember('uid:%s:following' % self.id, check_user_id):
            return True

        return False

    def follow(self, follow_user_id):
        r = RedisLink.factory()

        r.sadd('uid:%s:following' % self.id, follow_user_id)
        r.sadd('uid:%s:followers' % follow_user_id, self.id)

        self._add_to_news_following_posts(follow_user_id)

        return None

    def stop_following(self, follow_user_id):
        r = RedisLink.factory()

        r.srem('uid:%s:following' % self.id, follow_user_id)
        r.srem('uid:%s:followers' % follow_user_id, self.id)

        self._remove_from_news_following_posts(follow_user_id)

        return None

    def _remove_from_news_following_posts(self, follow_user_id):
        r = RedisLink.factory()
        posts_ids = r.lrange('uid:%s:posts' % follow_user_id, 0, -1)

        for post_id in posts_ids:
            r.zrem('uid:%s:news' % self.id, post_id)

        return None

    def _add_to_news_following_posts(self, follow_user_id):
        r = RedisLink.factory()
        posts = User.fetch_one(follow_user_id).get_posts(0, -1)

        for post in posts:
            r.zadd('uid:%s:news' % self.id, post['id'], int(post['create_time'].strftime('%s')))

        return None

    def count_followers(self):
        r = RedisLink.factory()
        return r.scard("uid:%s:followers" % self.id)

    def count_following(self):
        r = RedisLink.factory()
        return r.scard("uid:%s:following" % self.id)

    def _get_followers_ids(self):
        r = RedisLink.factory()
        return r.smembers('uid:%s:followers' % self.id)

    def add_post_to_followers_news(self, post_id, post_create_time):
        r = RedisLink.factory()

        follwers_ids = self._get_followers_ids()

        # Add the post to our own news too
        follwers_ids.add(self.id)

        for follower_user_id in follwers_ids:
            r.zadd("uid:%s:news" % follower_user_id, post_id, post_create_time)

    def create_auth(self):
        r = RedisLink.factory()

        authsecret = getrand()
        r.set("uid:%s:auth" % self.id, authsecret)
        r.set("auth:%s" % authsecret, self.id)

        return authsecret

    def destroy_auth(self):
        r = RedisLink.factory()

        authsecret = r.get('uid:%s:auth' % self.id)
        r.delete('auth:%s' % authsecret)
        r.delete('uid:%s:auth' % self.id)

    def get_posts(self, start, count):
        r = RedisLink.factory()
        posts_ids = r.lrange('uid:%s:posts' % self.id, start, start + count)

        return Post.get_posts_by_ids(posts_ids)

    def get_news(self, start, count):
        r = RedisLink.factory()
        posts_ids = r.zrevrange('uid:%s:news' % self.id, start, start + count)

        return Post.get_posts_by_ids(posts_ids)

    def __str__(self):
        return "User: {id: %s, username: %s}" % (self.id, self.username)

    @classmethod
    def fetch_one(cls, user_id):
        r = RedisLink.factory()

        username = r.get('uid:%s:username' % user_id)
        if not username:
            user_id = 0

        return cls(user_id, username)

    @classmethod
    def fetch_one_by_username(cls, username):
        r = RedisLink.factory()

        user_id = r.get('username:%s:id' % username)

        return cls(user_id, username)

    @classmethod
    def create_new(cls, username, password):
        r = RedisLink.factory()
        user_id = r.incr("global:nextUserId")

        r.set("username:%s:id" % username, user_id)

        r.set("uid:%s:username" % user_id, username)
        r.set("uid:%s:password" % user_id, password)

        # Manage a Set with all the users, may be userful in the future
        r.sadd("global:users", user_id)

        return cls.fetch_one(user_id)

    @classmethod
    def check_password(cls, username, password):
        r = RedisLink.factory()
        user_id = r.get('username:%s:id' % username)
        correct_password = r.get('uid:%s:password' % user_id)
        if password == correct_password:
            return user_id
        else:
            return False

    @staticmethod
    def get_all_usernames(start=0, num=10):
        r = RedisLink.factory()

        return r.sort('global:users', get='uid:*:username', desc=True, start=start, num=num)

    @staticmethod
    def check_auth_secret(auth_secret):
        r = RedisLink.factory()
        check_user_id = r.get('auth:%s' % auth_secret)
        correct_auth_secret = r.get('uid:%s:auth' % check_user_id)

        if correct_auth_secret == auth_secret:
            return check_user_id
        else:
            return False

#@todo Refactoring. Is Post realy needs to be depend on User?
class Post(object):
    @classmethod
    def add_post(cls, user_id, status, create_time=None):
        r = RedisLink.factory()
        postid = r.incr("global:nextPostId")

        if not create_time:
            create_time = time()

        create_time = int(create_time)

        post = "%s|%s|%s" % (user_id, create_time, status)
        r.set('post:%s' % postid, post)

        r.lpush("uid:%s:posts" % user_id, postid)

        r.lpush("global:timeline", postid)
        r.ltrim("global:timeline", 0, 1000)

        User.fetch_one(user_id).add_post_to_followers_news(postid, create_time)

    @classmethod
    def fetch_from_timeline(cls, start, count):
        r = RedisLink.factory()

        posts_ids = r.lrange('global:timeline', start, count)
        return cls.get_posts_by_ids(posts_ids)

    @classmethod
    def get_posts_by_ids(cls, posts_ids):
        r = RedisLink.factory()

        users_store = {}

        posts = []
        for post_id in posts_ids:
            post_str = r.get('post:%s' % post_id)
            (user_id, create_time, status) = post_str.split('|')

            if user_id in users_store:
                user = users_store[user_id]
            else:
                user = User.fetch_one(user_id)
                users_store[user_id] = user

            # @todo Maybe this should by Post object?
            posts.append({
                'id': post_id,
                'user_id': user_id,
                'create_time': datetime.fromtimestamp(float(create_time)),
                'status': status,
                'user': user
            })

        return posts

def getrand():
    # @todo Use normal some rand() function :)
    fd = open("/dev/urandom")
    data = fd.read(16)
    fd.close()
    return md5(data).hexdigest()
