import multiprocessing
import os

host = '[::1]'
port = 5000
workers = multiprocessing.cpu_count() * 2 + 1
if 'PORT' in os.environ:
    host = '0.0.0.0'
    port = int(os.environ['PORT'])

if 'WORKERS' in os.environ:
    workers = int(os.environ['WORKERS'])

bind = f'{host}:{port}'
worker_class = 'gevent'
