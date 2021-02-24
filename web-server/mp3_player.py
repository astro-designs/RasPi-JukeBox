import os
import sys
import urllib
import urllib2
import requests

print("Starting")

mp3_folder = '/media/JukeBox/'
mp3_file = sys.argv[1]

player_IP_Address = '127.0.0.1'
#player_IP_Address = 'raspi-jukebox'

command = 'omxplayer -o alsa ' + mp3_folder + mp3_file
os.system(command)

url = 'http://' + player_IP_Address + '/' + 'finished'
try:
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    playerFound = True
except urllib2.HTTPError, e:
    print e.code;
    playerFound = False
except urllib2.URLError, e:
    print e.args;
    playerFound = False

print("End of track!", playerFound)
