#! python3

import os
import platform
from importlib import reload

import schedule

import augentbot


def connect_run() -> None:
    os.system('git pull')
    if platform.system() == 'Windows':
        os.system('chcp 65001')  # fixes encoding errors on windows
    reload(augentbot)
    augentbot.run(create_buffers=1)


def simple_run() -> None:
    augentbot.run()


schedule.every().day.at('00:56').do(connect_run)
schedule.every().day.at('01:56').do(connect_run)
schedule.every().day.at('02:56').do(connect_run)
schedule.every().day.at('03:56').do(connect_run)
schedule.every().day.at('04:56').do(connect_run)
schedule.every().day.at('05:56').do(connect_run)
schedule.every().day.at('06:56').do(connect_run)
schedule.every().day.at('07:56').do(connect_run)
schedule.every().day.at('08:56').do(connect_run)
schedule.every().day.at('09:56').do(connect_run)
schedule.every().day.at('10:56').do(connect_run)
schedule.every().day.at('11:56').do(connect_run)
schedule.every().day.at('12:56').do(connect_run)
schedule.every().day.at('13:56').do(connect_run)
schedule.every().day.at('14:56').do(connect_run)
schedule.every().day.at('15:56').do(connect_run)
schedule.every().day.at('16:56').do(connect_run)
schedule.every().day.at('17:56').do(connect_run)
schedule.every().day.at('18:56').do(connect_run)
schedule.every().day.at('19:56').do(connect_run)
schedule.every().day.at('20:56').do(connect_run)
schedule.every().day.at('21:56').do(connect_run)
schedule.every().day.at('22:56').do(connect_run)
schedule.every().day.at('23:56').do(connect_run)

while True:
    schedule.run_pending()
