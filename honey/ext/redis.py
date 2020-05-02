"""
A module that implements a custom redis cache handler.
"""
from cement.ext.ext_redis import RedisCacheHandler


class HoneyRedisCacheHandler(RedisCacheHandler):
    """
    Override the default implementation to enable customizing the db meta
    """

    class Meta:

        """Handler meta-data."""

        label = 'redis'
        config_defaults = dict(
            host='127.0.0.1',
            port=6379,
            db=0,
            expire_time=0,
        )