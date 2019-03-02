import logging
from market_maker.settings import settings
from datetime import datetime
import os

def setup_custom_logger(name, log_level=settings.LOG_LEVEL):
    os.environ['TZ'] = 'Europe/Moscow'
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(handler)

    # date = datetime.today().strftime("%Y%m%d")
    # handler = logging.FileHandler('{}.log'.format(date))
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)

    return logger
