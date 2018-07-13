""" Decorator for cache-aware endpoints """
from functools import update_wrapper
import logging
import json
from flask import jsonify, request

import ytdl_audio_api.ytdl as ytdl


def get_in_cache(cache, key):
    cache_val = cache.get(key)
    if cache_val is not None:
        cache_val = json.loads(cache_val)
        return cache_val
    return None


def save_into_cache(cache, key, value, **kwargs):
    if 'timeout' in kwargs:
        cache.set(key, json.dumps(value), timeout=kwargs['timeout'])
    else:
        cache.set(key, json.dumps(value), **kwargs)


def cache_aware(cache, kkey, **kwargs_cache):
    """ Decorator that allows to create a JSON endpoint that stores values into the
    cache """

    def cache_aware2(func):
        def decorate(*args, **kwargs):
            nonlocal kkey
            nonlocal kwargs_cache
            for key in kwargs_cache:
                if callable(kwargs_cache[key]):
                    kwargs[key] = kwargs_cache[key]()
                else:
                    kwargs[key] = kwargs_cache[key]
            key = kkey.format(*args, **kwargs)
            cache_val = get_in_cache(cache, key)
            if cache_val is not None:
                logging.getLogger(__name__).debug('Found response in cache: %s -> %s', key, repr(cache_val))
                if 'error' in cache_val:
                    return as_json(cache_val), 404
                else:
                    return as_json(cache_val)

            try:
                val = func(*args, **kwargs)
                save_into_cache(cache, key, val, **kwargs_cache)
                logging.getLogger(__name__).debug('Saving response into cache: %s -> %s', key, repr(val))
                return as_json(val)
            except ytdl.YoutubeDLError as error:
                val = {'error': repr(error)}
                save_into_cache(cache, key, val)
                logging.getLogger(__name__).debug('Saving error response into cache: %s -> %s', key, repr(val))
                return as_json(val), 400

        return update_wrapper(decorate, func)

    return cache_aware2


def as_json(obj):
    response = jsonify(obj)
    response.obj = obj
    return response


def log_request(logger):
    def ahiva(func):
        def le_dec(*args, **kwargs):
            logger.info(f'[{request.remote_addr}] {request.method} {request.url}')
            return func(*args, **kwargs)
        return update_wrapper(le_dec, func)

    return ahiva
