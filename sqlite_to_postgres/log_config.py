"""Настройка логгера для двух хэндлеров: в stderr и файл."""

import logging

logger = logging.getLogger('etl_logger')
logger.setLevel(logging.INFO)
fh = logging.FileHandler('etl.log')
fh.setLevel(logging.ERROR)
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
sh.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(sh)
