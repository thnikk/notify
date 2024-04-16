# Notification scripts

## notify-twitch.py
Notifications when a streamer goes live. This just looks at a twitch page and extracts some json that says when the stream started. If the start date doesn't match the cached one, you get a notification.

### Setup
Create `~/.config/streamers` and put one streamer ID per line.

## notify-usb.py
Notifications for USB devices being plugged or unplugged. I do a lot of work with USB devices, so this is useful for debugging.

## notify-frigate.py
Notifications for frigate events. Requires MQTT to be enabled on frigate and a running mqtt broker. Accepts IP (and port with `-p`) as arguments.
