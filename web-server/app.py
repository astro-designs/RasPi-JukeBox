'''

RasPi-JukeBox - the Raspberry Pi JukeBox created by Mark Cantrill @Astro-Designs

To do...
    Add logging function
    Make it run under Python 3
    Prevent the playlist from falling over after 50 selections
    Flask - Turn off debugging
    Flask - Use a production thingy...
    Cleanup
    Test

'''
version = "1.0.31"

import os
import sys
import subprocess
import logging
import time
import RPi.GPIO as GPIO
import JukeBox_conf
from random import seed
from random import randint
from flask import Flask, render_template, request
app = Flask(__name__)

# Setup Log to file function
logfile = 'logs/' + time.strftime("%B-%d-%Y-%I-%M-%S%p") + '.log'
logger = logging.getLogger('myapp')
hdlr = logging.FileHandler(logfile)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

# Setup GPIO
GPIO.setmode(GPIO.BCM)

# Seed the random number generator
seed()

# Create an empty playlist
# Start with a minimum size of 10...
playlist = [0,0,0,0,0,0,0,0,0,0]

# Then increase the playlist to the desired length if needed
while len(playlist) < JukeBox_conf.playlist_Length:
    playlist.append(0)
    
# Reset playlist read / write pointers
playlist_write_pointer = 0
playlist_read_pointer = 0

# Variable to track if anything is currently playing
playing = False

# Search for Wallbox config file...
print("Searching for configuration file...")

# Initial configuration
num_letters = 0
num_numbers = 0
num_indexes = num_letters * num_numbers
rand_timeout = 0
config_file = ''
    
for model in JukeBox_conf.Wallbox_models:
    PATH = '/boot/' + JukeBox_conf.Wallbox_models[model]['filename']
    if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
        config_file = JukeBox_conf.Wallbox_models[model]['filename']
        wallbox_name = JukeBox_conf.Wallbox_models[model]['model']
        rand_timeout = JukeBox_conf.Wallbox_models[model]['rand_timeout']
        num_letters = JukeBox_conf.Wallbox_models[model]['num_letters']
        num_numbers = JukeBox_conf.Wallbox_models[model]['num_numbers']
        num_indexes = JukeBox_conf.Wallbox_models[model]['num_indexes']            
        break # Leave the loop as soon as the first model is identified

# Only proceed if a valid configuration file is found
if num_indexes == 0:
    message = "Error reading configuration file!"
    print(message)
    logger.info(message)
    sys.exit()
else:
    message = "Configuration: " + JukeBox_conf.Wallbox_models[model]['model']
    print(message)
    logger.info(message)

# Create a dictionary called pins to store the pin number, name, and pin state:
# Note: We don't actually need GPIO, these are present from the original Flask example by Matt Richardson and have been left here just in case we need to add some GPIO control...
pins = {
   23 : {'name' : 'GPIO 23', 'state' : GPIO.LOW},
   24 : {'name' : 'GPIO 24', 'state' : GPIO.LOW}
   }

# Set each pin as an output and make it low:
for pin in pins:
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.LOW)

# Create a dictionary of tracks based on what media files are found...
tracks = {}
for index in range(num_indexes):
    index_filename = '000' + str(index+1)
    index_filename = 'sel' + index_filename[-3:]
    index_filename = index_filename + '.mp3'

    # Create a new entry
    tracks[index+1] = {}    

    # Check if file exists...
    PATH = JukeBox_conf.media_folder + index_filename
    if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
        tracks[index+1]['filename'] = index_filename
        tracks[index+1]['title'] = 'Unknown'
        tracks[index+1]['artist'] = 'Unknown'
        tracks[index+1]['state'] = 'ready'
    else:
        tracks[index+1]['filename'] = index_filename
        tracks[index+1]['title'] = 'Unknown'
        tracks[index+1]['artist'] = 'Unknown'
        tracks[index+1]['state'] = 'NA'

@app.route("/")
def main():
   global playlist, playlist_write_pointer, playlist_read_pointer

   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)

   # Put the pin dictionary into the template data dictionary:
   templateData = {
      'version' : version,
      'logfile' : logfile,
      'playlist' : playlist,
      'playing_now' : playlist_read_pointer,
      'playing_queued' : playlist_write_pointer - playlist_read_pointer,
      'tracks' : tracks,
	  'pins' : pins
      }

   # Pass the template data into the template main.html and return it to the user
   return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with the pin number and action in it:
@app.route("/<changePin>/<action>")
def action(changePin, action):
   global playlist, playlist_write_pointer, playlist_read_pointer
   # Convert the pin from the URL into an integer:
   changePin = int(changePin)
   # Get the device name for the pin being changed:
   deviceName = pins[changePin]['name']
   # If the action part of the URL is "on," execute the code indented below:
   if action == "on":
      # Set the pin high:
      GPIO.output(changePin, GPIO.HIGH)
      # Save the status message to be passed into the template:
      message = "Turned " + deviceName + " on."
      logger.info(message)
   if action == "off":
      GPIO.output(changePin, GPIO.LOW)
      message = "Turned " + deviceName + " off."
      logger.info(message)

   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)

   templateData = {
      'version' : version,
      'logfile' : logfile,
      'playlist' : playlist,
      'playing_now' : playlist_read_pointer,
      'playing_queued' : playlist_write_pointer - playlist_read_pointer,
      'tracks' : tracks,
	  'pins' : pins
      }

   return render_template('main.html', **templateData)
   
# The function below is executed when the track being played ends
@app.route("/finished")
def finished():
   global playlist, playlist_write_pointer, playlist_read_pointer, playing
   
   # increment read pointer
   playlist_read_pointer = playlist_read_pointer + 1

   if playlist_read_pointer < playlist_write_pointer: # playlist has at least one entry ready to play

      # Identify filename of playlist item
      Track = '000' + str(playlist[playlist_read_pointer])
      Track = Track[-3:]
      
      # Play the next track...
      message = "Playing " + 'sel' + Track + '.mp3'
      print(message)
      logger.info(message)
      playing = True

      mp3_file = 'sel' + Track + '.mp3'
      subprocess.Popen(['python', 'mp3_player.py', mp3_file])
   else: # playlist is empty
      playing = False
      message = "End of Playlist."
      print(message)
      logger.info(message)

   templateData = {
      'version' : version,
      'logfile' : logfile,
      'playlist' : playlist,
      'playing_now' : playlist_read_pointer,
      'playing_queued' : playlist_write_pointer - playlist_read_pointer,
      'tracks' : tracks,
      'pins' : pins
      }

   return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with a track reference to add to the play list or play immediately
@app.route("/sel<changeTrack>/<action>")
def selection(changeTrack, action):
   global playlist, playlist_write_pointer, playlist_read_pointer, playing
   
   # Append zeros to changeTrack
   Track = '000' + str(changeTrack)
   Track = Track[-3:]
   if action == "play":
      message = "Playing " + Track
      playing = True
      mp3_file = 'sel' + Track + '.mp3'
      subprocess.Popen(['python', 'mp3_player.py', mp3_file])
   if action == "add":
      message = "Adding " + Track + " to Playlist."
      playlist[playlist_write_pointer] = int(changeTrack)
      playlist_write_pointer = playlist_write_pointer + 1
      
      # Start processing the playlist if nothing is playing
      if playing == False:
         if playlist_read_pointer < playlist_write_pointer: # playlist has at least one entry ready to play

            # Identify filename of playlist item
            Track = '000' + str(playlist[playlist_read_pointer])
            Track = Track[-3:]

            # Play the next track...
            message = "Playing " + 'sel' + Track + '.mp3'
            print(message)
            logger.info(message)
            playing = True
            mp3_file = 'sel' + Track + '.mp3'
            subprocess.Popen(['python', 'mp3_player.py', mp3_file])
         else: # playlist is empty
            playing = False
            message = "End of Playlist."
            print(message)
            logger.info(message)
      
   templateData = {
      'version' : version,
      'logfile' : logfile,
      'playlist' : playlist,
      'playing_now' : playlist_read_pointer,
      'playing_queued' : playlist_write_pointer - playlist_read_pointer,
      'tracks' : tracks,
      'pins' : pins
      }

   return render_template('main.html', **templateData)

# The function below is executed when someone requests a URL with a track reference to add to the play list or play immediately
@app.route("/random/<action>")
def random(action):
   # Find a random selection that's available
   attempt = 1
   changeTrack = randint(1,200)
   while tracks[changeTrack]['state'] != 'ready' and attempt <= 50:
      attempt = attempt + 1
      changeTrack = randint(1,200)

   if tracks[changeTrack]['state'] == 'ready':
      message = "Random selection: " + str(changeTrack)
      print(message)
      logger.info(message)
      # Pass the random selection together with the action to the selection function
      selection(changeTrack, action)   
   else:
      message = "Random selection failed after 50 attempts - tracks not ready"
      print(message)
      logger.info(message)

   templateData = {
      'version' : version,
      'logfile' : logfile,
      'playlist' : playlist,
      'playing_now' : playlist_read_pointer,
      'playing_queued' : playlist_write_pointer - playlist_read_pointer,
      'tracks' : tracks,
      'pins' : pins
      }

   return render_template('main.html', **templateData)
   
# The function below is executed when someone requests a URL a system call:
@app.route("/system/<action>")
def system(action):
   # If the action part of the URL is "on," execute the code indented below:
   if action == "shutdown":
      # Shutdown the player...
      message = "Shutting down..."
      print(message)
      logger.info(message)
      os.system("sudo shutdown") 
   elif action == "exit":
      # Exit the player to the command prompt...
      message = "Closing player..."
      print(message)
      logger.info(message)
      sys.exit()
   elif action == "reboot":
      # Exit the player to the command prompt...
      message = "Rebooting player..."
      print(message)
      logger.info(message)
      os.system("sudo reboot") 
   elif action == "ping":
      # Ping the player to check it's alive...
      message = "Received a Ping!"
      print(message)
      logger.info(message)

   templateData = {
      'version' : version,
      'logfile' : logfile,
      'playlist' : playlist,
      'playing_now' : playlist_read_pointer,
      'playing_queued' : playlist_write_pointer - playlist_read_pointer,
      'tracks' : tracks,
	  'pins' : pins
      }

   return render_template('main.html', **templateData)

logger.info('Starting RasPi-JukeBox...')

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)
