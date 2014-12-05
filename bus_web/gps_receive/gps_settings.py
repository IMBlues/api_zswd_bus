__author__ = 'blues'
import os
import sys

PROJECT_DIR_PATH = '/www/zq_bus/web'
sys.path.append(PROJECT_DIR_PATH)
os.environ['DJANGO_SETTINGS_MODULE'] = 'zq_bus.settings'

HOST = '0.0.0.0'
PORT = 12333
BUFSIZ = 1024
ERROR_VALUE = 0.000006
MAX_LENGTH = 21000000