import logging
from termcolor import colored
import datetime
import sys


def printer(color, title, message, over='on_white'):
    message = colored(message, color)
    title = colored(' {0:<6} '.format(title), color, over, attrs=['reverse'])

    now = datetime.datetime.now()
    date = colored(' {0} '.format(now.strftime("%H:%M:%S")), 'red', 'on_white')
    msg = ' '.join((''.join((title, date)), message))
    print msg