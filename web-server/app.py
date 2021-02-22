'''

Adapted excerpt from Getting Started with Raspberry Pi by Matt Richardson and with modifications from Rui Santos

Raspberry Pi JukeBox created by Mark Cantrill @Astro-Designs

'''

import os
import RPi.GPIO as GPIO
#import Jukebox
from flask import Flask, render_template, request
app = Flask(__name__)

GPIO.setmode(GPIO.BCM)

# Constants...
playlist_Length = 50

# Create an empty playlist
# Start with a minimum size of 10 then increase to the desired length
playlist = [0,0,0,0,0,0,0,0,0,0]
print("Playlist length: ",len(playlist))
while len(playlist) < playlist_Length:
    playlist.append(0)
    
# Reset playlist read / write pointers
playlist_write_pointer = 0
playlist_read_pointer = 0

print("Playlist length: ",len(playlist))
        

# Dictionary of supported configuration files
Wallbox_models = {
    1 : {'filename' : 'c0s01.cnf', 'rand_timeout' : 0, 'model' : 'Seeburg 3W1 / 3W100', 'num_letters' : 10, 'num_numbers' : 10, 'num_indexes' : 200},
    2 : {'filename' : 'c0s02.cnf', 'rand_timeout' : 0, 'model' : 'Seeburg 3W160', 'num_letters' : 16, 'num_numbers' : 10, 'num_indexes' : 160},
    3 : {'filename' : 'c0s03.cnf', 'rand_timeout' : 0, 'model' : 'Seeburg 3WA', 'num_letters' : 20, 'num_numbers' : 10, 'num_indexes' : 200},
    4 : {'filename' : 'c1s01.cnf', 'rand_timeout' : 30, 'model' : 'Seeburg 3W1 / 3W100', 'num_letters' : 10, 'num_numbers' : 10, 'num_indexes' : 200},
    5 : {'filename' : 'c1s02.cnf', 'rand_timeout' : 30, 'model' : 'Seeburg 3W160', 'num_letters' : 16, 'num_numbers' : 10, 'num_indexes' : 160},
    6 : {'filename' : 'c1s03.cnf', 'rand_timeout' : 30, 'model' : 'Seeburg 3WA', 'num_letters' : 20, 'num_numbers' : 10, 'num_indexes' : 200},
    7 : {'filename' : 'c2s01.cnf', 'rand_timeout' : 300, 'model' : 'Seeburg 3W1 / 3W100', 'num_letters' : 10, 'num_numbers' : 10, 'num_indexes' : 200},
    8 : {'filename' : 'c2s02.cnf', 'rand_timeout' : 300, 'model' : 'Seeburg 3W160', 'num_letters' : 16, 'num_numbers' : 10, 'num_indexes' : 160},
    9 : {'filename' : 'c2s03.cnf', 'rand_timeout' : 300, 'model' : 'Seeburg 3WA', 'num_letters' : 20, 'num_numbers' : 10, 'num_indexes' : 200},
    10 : {'filename' : 'c3s01.cnf', 'rand_timeout' : 900, 'model' : 'Seeburg 3W1 / 3W100', 'num_letters' : 10, 'num_numbers' : 10, 'num_indexes' : 200},
    11 : {'filename' : 'c3s02.cnf', 'rand_timeout' : 900, 'model' : 'Seeburg 3W160', 'num_letters' : 16, 'num_numbers' : 10, 'num_indexes' : 160},
    12 : {'filename' : 'c3s03.cnf', 'rand_timeout' : 900, 'model' : 'Seeburg 3WA', 'num_letters' : 20, 'num_numbers' : 10, 'num_indexes' : 200}
    }

# Search for Wallbox config file...
print("Searching for configuration file...")

num_letters = 0
num_numbers = 0
num_indexes = num_letters * num_numbers
rand_timeout = 0
config_file = ''
    
for model in Wallbox_models:
    PATH = '/boot/' + Wallbox_models[model]['filename']
    if os.path.isfile(PATH) and os.access(PATH, os.R_OK):
        config_file = Wallbox_models[model]['filename']
        wallbox_name = Wallbox_models[model]['model']
        rand_timeout = Wallbox_models[model]['rand_timeout']
        num_letters = Wallbox_models[model]['num_letters']
        num_numbers = Wallbox_models[model]['num_numbers']
        num_indexes = Wallbox_models[model]['num_indexes']            
        break

if num_indexes == 0:
    print("Error reading configuration file!")    
else:
    print("Configuration: " + Wallbox_models[model]['model'])

# Create a dictionary called pins to store the pin number, name, and pin state:
pins = {
   23 : {'name' : 'GPIO 23', 'state' : GPIO.LOW},
   24 : {'name' : 'GPIO 24', 'state' : GPIO.LOW}
   }

# Create a dictionary called tracks to store the track number, availability, track title and artist:

#tracks = {
#   1 : {'filename': 'sel001.mp3', 'title' : 'Unknown', 'artist' : 'Unknown', 'state' : 'ready'},
#   2 : {'filename': 'sel002.mp3', 'title' : 'Unknown', 'artist' : 'Unknown', 'state' : 'ready'},
#   3 : {'filename': 'NA', 'title' : 'Unknown', 'artist' : 'Unknown', 'state' : 'ready'},
#   4 : {'filename': 'sel003.mp3', 'title' : 'Unknown', 'artist' : 'Unknown', 'state' : 'ready'},
#   5 : {'filename': 'NA', 'title' : 'Unknown', 'artist' : 'Unknown', 'state' : 'ready'}
#   }

tracks = []
for index in range(5):
    index_filename = '000' + str(index+1)
    index_filename = 'sel' + index_filename[-3:]
    index_filename = index_filename + '.mp3'
    
    new_index = {'filename': index_filename, 'title' : 'Unknown', 'artist' : 'Unknown', 'state' : 'ready'}
    tracks.append(new_index)

print(len(tracks))
print(tracks[3])
print(tracks)
    
# Set each pin as an output and make it low:
for pin in pins:
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.LOW)

@app.route("/")
def main():
   global playlist, playlist_write_pointer, playlist_read_pointer
   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)
   # Put the pin dictionary into the template data dictionary:
   templateData = {
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
   if action == "off":
      GPIO.output(changePin, GPIO.LOW)
      message = "Turned " + deviceName + " off."

   # For each pin, read the pin state and store it in the pins dictionary:
   for pin in pins:
      pins[pin]['state'] = GPIO.input(pin)

   # Along with the pin dictionary, put the message into the template data dictionary:
   templateData = {
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
   global playlist, playlist_write_pointer, playlist_read_pointer
   if action == "play":
      #tracks[changeTrack]['state'] = 'Playing'
      message = "Playing " + changeTrack
      command = 'python mp3_player.py ' + 'sel' + changeTrack + '.mp3 ' + '&'
      os.system(command)
   if action == "add":
      message = "Adding " + changeTrack + " to Playlist."
      playlist[playlist_write_pointer] = int(changeTrack)
      print("Playlist[", playlist_write_pointer, "]: ", int(changeTrack))
      playlist_write_pointer = playlist_write_pointer + 1
      print("Next pos: ", playlist_write_pointer)

   # Along with the pin dictionary, put the message into the template data dictionary:
   templateData = {
      'playlist' : playlist,
      'playing_now' : playlist_read_pointer,
      'playing_queued' : playlist_write_pointer - playlist_read_pointer,
      'tracks' : tracks,
      'pins' : pins
      }

   return render_template('main.html', **templateData)

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=80, debug=True)
