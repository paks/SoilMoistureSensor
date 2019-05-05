import array
import math
import time
import board
from board import SCL, SDA, SPEAKER_ENABLE
import busio
import neopixel
from adafruit_seesaw.seesaw import Seesaw
from digitalio import DigitalInOut, Direction, Pull
from audioio import AudioOut, RawSample
#from adafruit_circuitplayground.express import cpx
 
i2c_bus = busio.I2C(SCL, SDA)

button = DigitalInOut(board.BUTTON_A)
button.direction = Direction.INPUT
button.pull = Pull.DOWN

speaker_enable = DigitalInOut(SPEAKER_ENABLE)
speaker_enable.direction = Direction.OUTPUT
speaker_enable.value = True

FREQUENCY = 440  # 440 Hz middle 'A'
SAMPLERATE = 8000  # 8000 samples/second, recommended!
#cpx.play_tone(800, 0.2)
# Generate one period of sine wav.
length = SAMPLERATE // FREQUENCY
sine_wave = array.array("H", [0] * length)
for i in range(length):
    sine_wave[i] = int(math.sin(math.pi * 2 * i / 18) * (2 ** 15) + 2 ** 15)
    
audio = AudioOut(board.SPEAKER)
sine_wave_sample = RawSample(sine_wave)
 

# Configure the soil sensor 
ss = Seesaw(i2c_bus, addr=0x36)

# This values need to be caligrated with the soil sensor
# The values below is what I got while testing the setup
# with dry dirt and wet dirt
cap_dry = 500
cap_wet = 900

dry = 0
dry_color = (255, 0 ,0)
normal = 1
normal_color = (0, 255, 0)
wet = 2
wet_color = (0, 0, 255)
black_color = (0, 0, 0)

pixels = neopixel.NeoPixel(board.NEOPIXEL, 10, brightness=.2)
pixels.fill(black_color)
pixels.show()

display = True

def soilTest(read):
    if (read < cap_dry):
        return dry
    elif (read > cap_wet):
        return wet
    else:
        return normal

previous_resul = dry

while True:
    # read moisture level through capacitive touch pad
    touch = ss.moisture_read()
     # read temperature from the temperature sensor
    temp = ss.get_temp()
    
    if button.value: # button pushed
        display = not display
        
    if display:
        result = soilTest(touch)
        if result == dry:
            pixels.fill(dry_color)
            if previous_resul != dry:
                previous_resul = dry
                audio.play(sine_wave_sample, loop=True)  # keep playing the sample over and over
                time.sleep(1)  # until...
                audio.stop()   # we tell the board to stop

        elif result == wet:
            previous_resul = wet
            pixels.fill(wet_color)
        else:
            previous_resul = normal
            pixels.fill(normal_color)
    else:
        pixels.fill(black_color)
    pixels.show()
    print("temp: " + str(temp) + "  moisture: " + str(touch))
    time.sleep(1)