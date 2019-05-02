import logging
import requests

from werkzeug.datastructures import Headers


def pipe(request, url, proxy=None):
    headers = {}
    if request.headers.get('Range'):
        headers['Range'] = request.headers.get('Range')
    proxies = {'http': proxy, 'https': proxy} if proxy is not None else None
    try:
        r = requests.get(url, headers=headers, proxies=proxies, stream=True)
        if r.status_code != 200:
            logging.getLogger(__name__).warning(f'http pipe failed for url {url} and proxy {proxy}: {r.status_code}')
            return None, None

        headers = Headers()
        headers.add('Content-Type', r.headers.get('Content-Type'))
        headers.add('Content-Length', r.headers.get('Content-Length'))
        headers.add('Accept-Ranges', 'bytes')
        headers.add('Content-Range', r.headers.get('Content-Range')) if request.headers.get('Range') else None

        return r.iter_content(4096), headers
    except Exception as e:
        logging.getLogger(__name__).exception(f'http pipe failed for url {url} and proxy {proxy}: {", ".join(e.args)}')
        return None, None


def pipe_headers(request, url, proxy=None):
    headers = {}
    if request.headers.get('Range'):
        headers['Range'] = request.headers.get('Range')
    proxies = { 'http': proxy, 'https': proxy } if proxy is not None else None
    try:
        r = requests.head(url, headers=headers, proxies=proxies)
        if r.status_code != 200:
            logging.getLogger(__name__).warning(f'http pipe failed for url {url} and proxy {proxy}: {r.status_code}')
            return None, None

        headers = Headers()
        headers.add('Content-Type', r.headers.get('Content-Type'))
        headers.add('Content-Length', r.headers.get('Content-Length'))
        headers.add('Accept-Ranges', 'bytes')
        headers.add('Content-Range', r.headers.get('Content-Range')) if request.headers.get('Range') else None
        return headers
    except Exception as e:
        logging.getLogger(__name__).exception(f'http pipe failed for url {url} and proxy {proxy}: {", ".join(e.args)}')
        return None
