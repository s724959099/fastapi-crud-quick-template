"""Log module"""
import datetime
import logging

from loguru import logger


class InterceptHandler(logging.Handler):
    """Customer Handler"""

    def emit(self, record):
        """override emit method"""
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level,
                                                               record.getMessage())


def setup_logging():
    """init logger"""
    logger.add(
        f'./logs/{datetime.date.today():%Y%m%d}.log',
        rotation='7 day',
        retention='28 days',
        level='INFO',
    )
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel('INFO')

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
