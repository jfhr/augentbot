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


if __name__ == '__main__':
    schedule.every().day.at('00:26').do(connect_run)
    schedule.every().day.at('01:26').do(connect_run)
    schedule.every().day.at('02:26').do(connect_run)
    schedule.every().day.at('03:26').do(connect_run)
    schedule.every().day.at('04:26').do(connect_run)
    schedule.every().day.at('05:26').do(connect_run)
    schedule.every().day.at('06:26').do(connect_run)
    schedule.every().day.at('07:26').do(connect_run)
    schedule.every().day.at('08:26').do(connect_run)
    schedule.every().day.at('09:26').do(connect_run)
    schedule.every().day.at('10:26').do(connect_run)
    schedule.every().day.at('11:26').do(connect_run)
    schedule.every().day.at('12:26').do(connect_run)
    schedule.every().day.at('13:26').do(connect_run)
    schedule.every().day.at('14:26').do(connect_run)
    schedule.every().day.at('15:26').do(connect_run)
    schedule.every().day.at('16:26').do(connect_run)
    schedule.every().day.at('17:26').do(connect_run)
    schedule.every().day.at('18:26').do(connect_run)
    schedule.every().day.at('19:26').do(connect_run)
    schedule.every().day.at('20:26').do(connect_run)
    schedule.every().day.at('21:26').do(connect_run)
    schedule.every().day.at('22:26').do(connect_run)
    schedule.every().day.at('23:26').do(connect_run)

    while True:
        schedule.run_pending()
