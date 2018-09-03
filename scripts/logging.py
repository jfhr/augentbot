#! python3.6

from sys import stdout
import logging

from .config import *

handler_console = logging.StreamHandler(stdout)
handler_console.setFormatter(logging.Formatter('{asctime}: {msg}'))
handler_console.setLevel(logging.INFO)

handler_file = logging.FileHandler(LOG_FILE)
handler_file.setFormatter('{asctime} [{module}->{funcName}:{lineno}] {msg}')
handler_file.setLevel(logging.DEBUG)


class TwitterDMHandler(logging.Handler):
    # sends log messages via twitter notification
    def __init__(self, twitter_api):
        super().__init__(self)
        self.api = twitter_api

    def emit(self, record):
        """
        send a message to the user specified as HOST_NAME. Messages longer than 10000
        characters will be split in sub-messages due to twitter limits
        """
        for subtext in [record[i:i + 10000] for i in range(0, len(record), 10000)]:
            self.api.send_direct_message(screen_name=HOST_NAME, text=subtext)


def get_logger(twitter_api) -> logging.Logger:
    handler_dm = TwitterDMHandler(twitter_api)
    handler_dm.setFormatter('Module: {module}\nFunction: {funcName}\nLine: {lineno}\n\n{msg}')
    handler_dm.setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.addHandler(handler_console)
    logger.addHandler(handler_file)
    logger.addHandler(handler_dm)

    return logger
