#!/usr/bin/python3 -u
"""
Description: Get a notification when there's a new Frigate event
Author: thnikk
"""
import os
import time
import subprocess
from datetime import datetime
import json
import argparse
from paho.mqtt import client as mqtt
from paho.mqtt import subscribe

# Configurable
snapshot = os.path.expanduser("~/.cache/snapshot.jpg")


def parse_args() -> argparse.ArgumentParser:
    """ Parse arguments """
    parser = argparse.ArgumentParser()
    parser.add_argument('IP')
    parser.add_argument('-p', '--port', type=int, default=1883)
    return parser.parse_args()


def on_connect(client, userdata, flags, result_code):
    """ What to do when connecting to mqtt server """
    del userdata, flags
    print("Connected with result code "+str(result_code))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("frigate/events")


def on_message(client, userdata, msg):
    """ What to do when a new message is published """
    del userdata
    data = json.loads(msg.payload)
    if data['type'] == 'new':
        # Add a delay to give frigate some time to take a snapshot
        time.sleep(2)
        now = f"[{datetime.now():%I:%M:%S%P %m-%d-%Y}]"
        print(f"{now} Person detected at door.")

        image = subscribe.simple(
            'frigate/door/person/snapshot',
            hostname=client._host, port=client._port)

        with open(snapshot, "wb") as snapshot_file:
            snapshot_file.write(image.payload)  # pylint: disable=no-member
        subprocess.run(
            ['notify-send', "-i", snapshot, "-c", "frigate", "Frigate",
                f"{now}\nPerson detected at door."], check=False)
        subprocess.run(
            ["paplay", "/usr/share/sounds/freedesktop/stereo/message.oga"],
            check=False)


def main():
    """ Main function """
    args = parse_args()
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(args.IP, args.port)
    client.loop_forever()


if __name__ == "__main__":
    main()
