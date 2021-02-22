'''

Raspberry Pi JukeBox created by Mark Cantrill @Astro-Designs
Configuration file

'''
import RPi.GPIO as GPIO

# Constants...
playlist_Length = 50

# Media folder
media_folder = '/media/JukeBox/'

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

# Create a dictionary called pins to store the pin number, name, and pin state:
# Note: We don't actually need GPIO, these are present from the original example by Matt Richardson and have been left here just in case we need to add some GPIO control...
pins = {
   23 : {'name' : 'GPIO 23', 'state' : GPIO.LOW},
   24 : {'name' : 'GPIO 24', 'state' : GPIO.LOW}
   }
