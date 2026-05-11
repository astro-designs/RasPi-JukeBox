Raspberry Pi JukeBox

Installation:
Install Raspbian on an 8GB or larger MicroSD card
Note: This has been tested with Raspberry Pi O/S with Desktop, release  4th March, 2021
Note: Using the version without recommended software so that it fits onto an 8GB micro-SD card

Connect the 8GB (or larger) micro-SD card to the Raspberry Pi, connect keyboard, HDMI monitor, keyboard & mouse (mouse not essential), using adapters for the micro HDMI & USB connectors.
Go through the initial setup, making sure you complete the WiFi setup as WiFi is essential.
    1) After initial boot, press 'Next' to continue through setup
    2) Setup Country, pressing 'Next' to continue
    3) Change password, setting a new password, pressing 'Next' to continue
    4) Setup Screen, just press 'Next' to continue as we don't need the screen
    5) Update Software - press 'Skip' to jump over this step;
    6) Setup Complete - press 'Done' to finish the setup.
    7) Setup WiFi
        a) 
    8) Preferences - make the following changes to the default:
        a) Raspberry Pi Configuration:
            i) Hostname: RasPi-Jukebox
            ii) Boot: To CLI
            iii) Auto Login: Disabled
            iv) Interfaces: Enable SSH
            v) Take a moment to check the location setup is correct and changes as required
            vi) Click on 'OK' to accept the changes and then press 'OK' to reboot.
            
Software installation:
All of the software for running the Jukebox function is available in a Git repository which should be cloned to the Raspberry Pi

1) Login as user 'pi'
2) Clone the RasPi-JukeBox repository
    sudo git clone https://github.com/astro-designs/RasPi-JukeBox.git

Configure the Pi to run the Jukebox software at startup:
1) Install a new cron job
1a) Open crontab:
    crontab -e
1b) Select your favorite editor (nano is always a good start here...)
1c) Add the following command to the last line:
    @reboot /home/pi/jukebox-launcher.sh
	The launcher automatically calls a git-pull function to ensure the local files are up-to-date with the files on GitHub
1d) Press ctrl-x to exit and select 'Y' to save
    
Installation complete!

Tip - test the installation by manually running the following:
sudo python /home/pi/RasPi-Jukebox/web-server/app.py




Typical low time: 90ms
Typical high time 60ms
high time between alpha-numeric sections: 430ms
