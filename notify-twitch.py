#!/usr/bin/python3 -u
"""
Description: Get notified of live twitch streams
Author: thnikk
"""
from subprocess import Popen
import json
import os
import argparse
import time
import requests
from common import Schedule


def get_args():
    """ Get command line arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action='store_true', help='Force notifications')
    return parser.parse_args()


def notify(subject, body) -> None:
    """ Send notifications """
    # pylint: disable=consider-using-with
    Popen(['paplay', '/usr/share/sounds/freedesktop/stereo/message.oga'])
    Popen(["notify-send", subject,
           body.encode('unicode-escape').decode('utf-8'), "--action",
           "default=open"])


def cache_save(path, contents) -> None:
    """ Save cache to file """
    with open(path, 'w', encoding='utf-8') as file:
        file.write(json.dumps(contents, indent=4))


def cache_load(path) -> dict:
    """ Load cache from file """
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


def get_streamer_list(path) -> list:
    """ Load list of streamers separated by line """
    with open(path, 'r', encoding='utf-8') as file:
        return file.read().strip().splitlines()


def strip_emojis(string) -> str:
    """ Strip emojis from descriptions """
    encoded = string.encode('unicode-escape').decode('utf-8')
    formatted = " ".join([
        word for word in encoded.split(' ') if '\\x' not in word and word
    ])
    return formatted


def get_json(streamer) -> dict:
    """ Get json from stream """
    response = requests.get(
        f'https://twitch.tv/{streamer}',
        timeout=3
    ).text
    for line in response.split('><'):
        if 'application/ld+json' in line:
            return json.loads(line.split('>')[1].split('<')[-2])[0]
    raise ValueError


def network_test() -> bool:
    """ Check connection """
    for x in range(1, 5):
        del x
        try:
            requests.get('https://twitch.tv', timeout=3)
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(3)
    return False


def notify_twitch() -> None:
    """ Main function """
    args = get_args()
    streamers = get_streamer_list(os.path.expanduser('~/.config/streamers'))
    cache_file = os.path.expanduser("~/.cache/notify-twitch.json")

    current_status = {streamer: {} for streamer in streamers}

    # If a connection can't be established, skip scheduled loop
    if not network_test():
        return

    try:
        cache = cache_load(cache_file)
    except FileNotFoundError:
        cache = current_status.copy()

    for streamer in streamers:
        try:
            current_status[streamer] = get_json(streamer)
        except ValueError:
            continue

        try:
            if current_status[streamer]['publication']['startDate'] != \
                    cache[streamer]['publication']['startDate'] or args.f:
                raise ValueError
        except (KeyError, ValueError):
            notify(f"{streamer} is live!", strip_emojis(
                current_status[streamer]['description']))
            cache[streamer] = current_status[streamer]

        time.sleep(1)

    cache_save(cache_file, cache)


def main():
    """ Schedule loop """
    sched = Schedule(5)
    sched.loop(notify_twitch)


if __name__ == "__main__":
    main()
