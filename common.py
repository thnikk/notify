#!/usr/bin/python3 -u
"""
Description:
Author:
"""
from subprocess import run, Popen, CalledProcessError
from datetime import datetime, timedelta
import time


def notify(subject, body, file=None, sound="message") -> None:
    """ Create notification """
    try:
        if not file:
            raise ValueError
        prog = Popen(['notify-send.sh', f'--replace-id={file}', subject, body])
    except (FileNotFoundError, ValueError):
        prog = Popen(['notify-send', subject, body])

    sounds = {
        "add": "/usr/share/sounds/freedesktop/stereo/power-plug.oga",
        "remove": "/usr/share/sounds/freedesktop/stereo/power-unplug.oga",
        "message": "/usr/share/sounds/freedesktop/stereo/message.oga"
    }
    if sound:
        Popen(['paplay', sounds[sound]])
    print(prog.returncode)


class Schedule():
    """ Schedule """
    def __init__(self, mins):
        self.time_diff = timedelta(minutes=mins)
        self.start = datetime.now() - self.time_diff

    def ready(self):
        """ Check if ready"""
        return (datetime.now() - self.start) > self.time_diff

    def update(self):
        """ Update current time """
        self.start = datetime.now()

    def loop(self, function):
        while True:
            if self.ready():
                function()
                self.update()
            time.sleep(1)
