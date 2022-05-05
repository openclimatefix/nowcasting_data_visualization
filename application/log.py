import logging
import os
from logging import config


def _get_logger():
    """ Create a logger """
    # create logger
    logger = logging.getLogger('Data vis')
    logger.setLevel(getattr(logging, os.environ.get("LOG_LEVEL", "DEBUG")))

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(getattr(logging, os.environ.get("LOG_LEVEL", "DEBUG")))

    # create formatter
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(module)s : %(funcName)s : %(lineno)d : %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger

logger = _get_logger()
