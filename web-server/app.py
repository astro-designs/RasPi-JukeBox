'''

Raspberry Pi JukeBox created by Mark Cantrill @Astro-Designs

'''

import os
import RPi.GPIO as GPIO
import JukeBox_conf
from flask import Flask, render_template, request
app = Flask(__name__)

GPIO.setmode(GPIO.BCM)

# Create an empty playlist
# Start with a minimum size of 10...
playlist = [0,0,0,0,0,0,0,0,0,0]

# Then increase the playlist to the desired length if needed
while len(playlist) < JukeBox_conf.playlist_Length:
    playlist.append(0)
    
# Reset playlist read / write pointers
playlist_write_pointer = 0
playlist_read_pointer = 0

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
    print("Error reading configuration file!")
    print("Please check the configuration file.")
    sys.exit()
else:
    print("Configuration: " + JukeBox_conf.Wallbox_models[model]['model'])

# Create a dictionary called pins to store the pin number, name, and pin state:
# Note: We don't actually need GPIO, these are present from the original example by Matt Richardson and have been left here just in case we need to add some GPIO control...
pins = {
   23 : {'name' : 'GPIO 23', 'state' : GPIO.LOW},
   24 : {'name' : 'GPIO 24', 'state' : GPIO.LOW}
   }

tracks = {}
for index in range(num_indexes):
    index_filename = '000' + str(index+1)
    index_filename = 'sel' + index_filename[-3:]
    index_filename = index_filename + '.mp3'

    # Create a new entry
    tracks[index+1] = {}    

    # Check if file exists...
    PATH = JukeBox_conf.media_folder + index_filename
    print(PATH)
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
   
   # Append zeros to changeTrack
   Track = '000' + str(changeTrack)
   Track = Track[-3:]
   if action == "play":
      message = "Playing " + Track
      command = 'python mp3_player.py ' + 'sel' + Track + '.mp3 ' + '&'
      os.system(command)
   if action == "add":
      message = "Adding " + Track + " to Playlist."
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
