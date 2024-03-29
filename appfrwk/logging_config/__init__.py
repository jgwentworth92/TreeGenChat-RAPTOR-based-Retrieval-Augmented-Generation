"""
Logging configuration for application
"""
import logging
import os
import sys
import multiprocessing

from logging.config import dictConfig
from appfrwk.logging_config.log_formatters import JsonFormatter

from appfrwk.config import get_config

config = get_config()
APP_NAME = config.APP_NAME
LOG_DIR = config.LOG_DIRECTORY
DEUBG = config.DEBUG

# Create log directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def setup_logging():
    """ 
    Setup logging configuration
    """
    dictConfig(LOGGING_CONFIG)

def get_logger(logger_name=APP_NAME, module_name=None):
    """
    Get logger by name or module name
    """
    # if name is multiprocessing, use multiprocessing logger (temp)
    if logger_name == 'multiprocessing':
        return get_multiprocessing_logger()
    # if module_name is passed, use module_name
    if module_name:
        return logging.getLogger(logger_name or APP_NAME).getChild(module_name)
    else:
        return logging.getLogger(logger_name)

def get_multiprocessing_logger():
    """
    Get multiprocessing logger
    """
    logger = multiprocessing.get_logger
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.handlers[0].setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
    logger.propagate = False
    logger.addHandler(logging.FileHandler(os.path.join(LOG_DIR, 'multiprocessing.log')))
    return logger

# Define the logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    # define the format of the log messages
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        # json formatter grabbed from log_formatters
        'json' : {
            '()': 'appfrwk.logging_config.log_formatters.JsonFormatter',
        },
    },
    # define handlers
    'handlers': {
        'console': {
            # log to stdout
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout',
            'level': 'DEBUG',
        },
        # RotatingFileHandler allows for log rotation after a certain size
        'file':{
            'class': 'logging.handlers.RotatingFileHandler',
            # for now, using standard formatter
            'formatter': 'standard',
            'filename': os.path.join(LOG_DIR, f'{APP_NAME}.log'),
            'maxBytes': 5000000,
            'backupCount': 5,
        },
        'request':{
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'json',
            'filename': os.path.join(LOG_DIR, f'request.log'),
            'maxBytes': 5000000,
            'backupCount': 5,
        }, # request_processing handler uses the same file as request
        'request_processing':{
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': os.path.join(LOG_DIR, f'request_processing.log'),
            'maxBytes': 5000000,
            'backupCount': 5,
        },
        'multiprocessing':{
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': os.path.join(LOG_DIR, f'multiprocessing.log'),
            'maxBytes': 5000000,
            'backupCount': 5,
        },
    },
    # defining loggers
    'loggers': {
        # root logger
        '': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False
        },
        # app logger
        f'{APP_NAME}': {
            'handlers': ['console','file'],
            'level': 'DEBUG',
            'propagate': False
        },
        # request logger uses json formatter
        'request': {
            # leaving console just to see if this works
            'handlers': ['console','request'],
            'level': 'DEBUG',
            'propagate': False
        },
        # request processing logger uses standard formatter
        'request_processing': {
            'handlers': ['request_processing'],
            'level': 'DEBUG',
            'propagate': False
        },
        # multiprocessing logger
        'multiprocessing': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
    },
    }
}