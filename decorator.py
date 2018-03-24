""" Decorator for cache-aware endpoints """
from functools import update_wrapper
import json
from flask import jsonify
from werkzeug.contrib.cache import SimpleCache

import ytdl


cache = SimpleCache()


def get_in_cache(key):
    global cache
    cache_val = cache.get(key)
    if cache_val is not None:
        cache_val = json.loads(cache_val)
        return cache_val
    return None

def save_into_cache(key, value, **kwargs):
    global cache
    cache.set(key, json.dumps(value), **kwargs)

def cache_aware(kkey, **kwargs_cache):
    """ Decorator that allows to create a JSON endpoint that stores values into the
    cache """
    def cache_aware2(func):
        def decorate(*args, **kwargs):
            nonlocal kkey
            nonlocal kwargs_cache
            key = kkey.format(*args, **kwargs)
            cache_val = get_in_cache(key)
            if cache_val is not None:
                if 'error' in cache_val:
                    return jsonify(cache_val), 404
                else:
                    return jsonify(cache_val)

            try:
                val = func(*args, **kwargs)
                save_into_cache(key, val, **kwargs_cache)
                return jsonify(val)
            except ytdl.YoutubeDLError as error:
                val = {'error': repr(error)}
                save_into_cache(key, val)
                return jsonify(val), 400
        return update_wrapper(decorate, func)
    return cache_aware2
