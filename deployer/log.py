import logging


class DeployerLogger(object):

    def __init__(self, loggerName):
        # create logger
        self.loggerName = loggerName
        logger = logging.getLogger(loggerName)
        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)

    def getLogger(self):
        return logging.getLogger(self.loggerName)