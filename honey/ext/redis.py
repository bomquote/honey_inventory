"""
A module that implements a custom redis cache handler.
"""
import redis
from cement.ext.ext_redis import RedisCacheHandler


class HoneyRedisCacheHandler(RedisCacheHandler):
    """
    Override the default implementation to enable customizing the db meta
    """

    class Meta:

        """Handler meta-data."""

        label = 'redis'
        config_section = 'cache.redis'

    def __init__(self, *args, **kw):
        super(HoneyRedisCacheHandler, self).__init__(*args, **kw)
        self.mc = None

    def _setup(self, *args, **kw):
        super(HoneyRedisCacheHandler, self)._setup(*args, **kw)
        if self._config('USE_PASSWORD'):
            self.r = redis.StrictRedis(
                host=self._config('HOST'),
                port=self._config('PORT'),
                db=self._config('DB'),
                password=self._config('PASSWORD'))
        else:
            self.r = redis.StrictRedis(
                host=self._config('HOST'),
                port=self._config('PORT'),
                db=self._config('DB'))
