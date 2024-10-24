import os
import logging
from logging.handlers import RotatingFileHandler

dir_path = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join(dir_path, "./logs/moonshine.log")


logger = logging.getLogger("")
logger.setLevel(logging.WARNING)
handler = RotatingFileHandler(log_path, maxBytes=20000, backupCount=10)
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
