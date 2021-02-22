import os
import sys

print("Starting")

mp3_folder = '/media/JukeBox/'
mp3_file = sys.argv[1]

command = 'omxplayer -o alsa ' + mp3_folder + mp3_file
os.system(command)
print("Finished")
