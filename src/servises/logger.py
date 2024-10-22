import logging


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    :param name: The name of the logger to be created.
    :param level: The logging level, default is logging.INFO.
    :return: The configured logger instance.
    """

    logger = logging.getLogger(name)

    if not logger.hasHandlers():

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s - Line: %(lineno)d')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger
