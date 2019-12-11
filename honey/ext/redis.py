"""
A module that implements a custom redis cache handler.
"""
from cement.ext.ext_redis import RedisCacheHandler


class HoneyRedisCacheHandler(RedisCacheHandler):
    """
    Override the default implementation meta to set the redis db to 1
    """

    class Meta:

        """Handler meta-data."""

        label = 'redis'
        config_defaults = dict(
            host='127.0.0.1',
            port=6379,
            db=1,
            expire_time=0,
        )