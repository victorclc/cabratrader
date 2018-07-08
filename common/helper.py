from pathlib import Path
import json
import logging
import re


def load_config(name):
    config = 'config/{}'.format(name)
    local = 'localconfig/{}'.format(name)

    config_path = Path(config)
    if not config_path.is_file():
        raise FileNotFoundError

    with open(config) as fp:
        json_config = json.load(fp)

    local_path = Path(local)
    if local_path.is_file():
        with open(local) as fp:
            other_config = json.load(fp)

        for key, value in other_config.items():
            json_config[key] = value

    return json_config


def load_logger(name):
    log4p = load_config("log4p.cfg")
    config = log4p[name]
    path = config['file']
    mode = config['mode']
    level = config['level']
    fmt = config['format']
    stream = config['stream']

    logger = logging.getLogger(name)
    formatter = logging.Formatter(fmt)
    file_handler = logging.FileHandler(path, mode=mode)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if stream:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    logger.setLevel(level)
    return logger


def load_analyser(relative_path):
    with open('analysis/{}'.format(relative_path)) as fp:
        exec(fp.read())
        return locals()['d_analysis']


class Constants(object):
    call_logger = load_logger('CallStalker')


def callstalker(func):
    def wrapper(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            Constants.call_logger.debug("{}{} -> {}".format(func.__name__, args, ret.__dict__ if ret else ret))
            return ret
        except Exception as ex:
            Constants.call_logger.error("{}{} -> {}".format(func.__name__, args, ex))
            raise ex

    return wrapper


def config2seconds(cfg):
    config = {
        'M': 30 * 24 * 60 * 60,
        'D': 24 * 60 * 60,
        'h': 60 * 60,
        'm': 60,
        's': 1
    }
    return int(re.search(r'\d+', cfg).group()) * config[cfg[-1]]
