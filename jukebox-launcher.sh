#!/bin/bash

# Export GPIO pins for LEDs
echo 20 > /sys/class/gpio/export 2>/dev/null
echo 23 > /sys/class/gpio/export 2>/dev/null

# Set them as outputs
echo out > /sys/class/gpio/gpio20/direction
echo out > /sys/class/gpio/gpio23/direction

# Turn LEDs ON to show update is running
echo 1 > /sys/class/gpio/gpio20/value
echo 1 > /sys/class/gpio/gpio23/value

echo "$(date) - Jukebox Launcher started..." >> /home/pi/jukebox.log
echo "$(date) - Jukebox Launcher started..." | wall



# Wait up to 30 seconds for WiFi to come up
echo "Waiting for network / internet connection..." >> /home/pi/jukebox.log
for i in {1..30}; do
    if ping -c 1 -W 1 github.com >/dev/null 2>&1; then
        echo "Network is up at $(date)" >> /home/pi/jukebox.log
        break
    fi
    sleep 1

    echo "$(date) - Network connection failed to appear" >> /home/pi/jukebox.log
done

cd /home/pi/RasPi-JukeBox

# Check WiFi connection...
iwgetid >> /home/pi/jukebox.log 2>&1

# Make sure git is available...
if command -v git >/dev/null 2>&1; then
    echo "Updating Jukebox code from GitHub..." >> /home/pi/jukebox.log
    echo "Updating Jukebox code from GitHub..." | wall
    git fetch --all >> /home/pi/jukebox.log 2>&1
    git reset --hard origin/master >> /home/pi/jukebox.log 2>&1
    #git clean --fd # Commented out as this will remove logs and any history of any reported problems

    echo "Jukebox project files update completed!" >> /home/pi/jukebox.log
    echo "Jukebox project files update completed!" | wall
else
    echo "Jukebox project files update failed - git not installed!" >> /home/pi/jukebox.log
    echo "Jukebox project files update failed - git not installed!" | wall
fi

# Turn LEDs OFF after update completes
echo 0 > /sys/class/gpio/gpio20/value
echo 0 > /sys/class/gpio/gpio23/value
echo 20 > /sys/class/gpio/unexport
echo 23 > /sys/class/gpio/unexport

# Run the Wallbox script
cd web-server
sudo python app.py

