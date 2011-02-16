import redis

#@todo is it correct use class attr for redis link? (Mulitithreading safe?)
class RedisLink(object):
    redis = 0

    @classmethod
    def factory(cls, *args, **kwargs):
        if not cls.redis:
            cls.redis = redis.Redis(*args, **kwargs)

        return cls.redis
