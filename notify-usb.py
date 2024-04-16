#!/usr/bin/python3 -u
"""
Simple python script for showing notifications for connected/disconnected
USB devices.
"""
import subprocess
import argparse
import os
from datetime import datetime
import pyudev

parser = argparse.ArgumentParser(
        description="Create notifications on USB events")
parser.add_argument(
        '-s', action="store_true", help='Enable sound on notification')
args = parser.parse_args()

# Set up pyudev
context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by(subsystem='usb')

replace_id = (
    f"--replace-file={os.path.expanduser('~/.cache/usb-notify.replace-id')}")


# Create a dictionary for state info
states = {
    "add": {
        "icon": "",
        "sound": "/usr/share/sounds/freedesktop/stereo/power-plug.oga",
        "text": "Connected",
    },
    "remove": {
        "icon": "",
        "sound": "/usr/share/sounds/freedesktop/stereo/power-unplug.oga",
        "text": "Disconnected",
    },
}


def notify(state, model, last_sound):
    """ Show notification and play a sound on state change """
    subprocess.run([
        'notify-send.sh',
        replace_id,
        f'{states[state]["icon"]} {states[state]["text"]} {model}'
    ], check=True)
    if args.s:
        # Don't play a sound more than once every 2 seconds
        if (datetime.now() - last_sound).total_seconds() > 2:
            last_sound = datetime.now()
            subprocess.run(
                ['pw-play', states[state]["sound"]], check=True)


def get_id(devices, device):
    """ Get name of device """
    try:
        model = device.get('ID_USB_MODEL').replace("_", " ")
        # Load from cache if device doesn't return model
        if model is None:
            model = devices[device.device_path]
        # Otherwise, update the cache
        else:
            devices[device.device_path] = model
    except (AttributeError, KeyError):
        pass


def main():
    """ Main function """
    # Store time of last played notification sound
    last_sound = datetime.now()

    # Cache device IDs because they disappear when unplugged
    devices = {}

    # Initialize device cache
    for device in context.list_devices(subsystem='usb'):
        try:
            model = device.get('ID_USB_MODEL').replace("_", " ")
            devices[device.device_path] = model
        # pass if ID_USB_MODEL returns nothing
        except AttributeError:
            pass

    # Poll for events
    for device in iter(monitor.poll, None):
        # On add/remove
        if device.action == 'add':
            try:
                # print(device.sys_name, device.sys_path, device.sys_number)
                # print(device.tags, device.subsystem, device.driver)
                # Look for device name
                model = device.get('ID_USB_MODEL').replace("_", " ")
                if "hub" in model.lower() or "host" in model.lower():
                    continue
                # Update cache with new device
                devices[device.device_path] = model
                # Create notification
                notify(device.action, model, last_sound)
            # Skip if the device doesn't have the ID_USB_MODEL property
            except AttributeError:
                pass
        if device.action == 'remove':
            try:
                # Get model from cache
                model = devices[device.device_path]
                if "hub" in model.lower():
                    continue
                # Create notification
                notify(device.action, model, last_sound)
            # Skip if device isn't in cache
            except KeyError:
                pass


if __name__ == "__main__":
    main()
