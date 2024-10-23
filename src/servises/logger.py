import logging


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Configures and returns a logger instance.

    This function creates a logger with the specified name and level. If the logger does not already have handlers,
    it will create a console handler that outputs log messages to the standard output. The log messages will include
    the timestamp, logger name, log level, message content, the filename, and the line number from where the log was
    generated. The default logging level is set to INFO, which means that it will capture all messages of level INFO
    and higher (WARNING, ERROR, CRITICAL).

    :param name: The name of the logger to be created.
    :type name: str
    :param level: The logging level, default is logging.INFO. This determines the severity of messages that the logger will handle.
    :type level: int
    :return: The configured logger instance.
    :rtype: logging.Logger

    """

    logger = logging.getLogger(name)

    if not logger.hasHandlers():

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s - Line: %(lineno)d')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)

    return logger
