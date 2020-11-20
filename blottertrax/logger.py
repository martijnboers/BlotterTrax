import logging


class Logger:
    def __init__(self):
        # create logger with 'spam_application'
        self.logger = logging.getLogger('blotter-trax')
        self.logger.setLevel(logging.DEBUG)

        if self.logger.hasHandlers() is True:
            return

        fh = logging.FileHandler('debug.log')
        fh.setLevel(logging.DEBUG)

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s :%(levelname)s: %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # add the handlers to the logger
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)

    def exception(self, message: str):
        self.logger.exception(message)
