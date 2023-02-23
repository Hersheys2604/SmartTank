import matplotlib.pyplot as plt
import time
import random
import math
from pymata4 import pymata4

#Arduino and pn set up
myArduino = pymata4.Pymata4()

triggerPin = 7 
myArduino.set_pin_mode_digital_output(triggerPin)
inputPin = 3 
myArduino.set_pin_mode_analog_input(inputPin)
myArduino.digital_write(7, 1)
# myArduino.digital_write(7, 0)
time.sleep(0.5)
start = time.time()
while True:
    print(myArduino.analog_read(3))
    if myArduino.analog_read(3)[0] < 10:
        end = time.time()
        print(end-start)
        numb = int(input('1 or 2:'))
        if numb == 1:
            myArduino.shutdown()
            break
        else:
            myArduino.digital_write(7, 0)
            myArduino.digital_write(7, 1)
            time.sleep(0.5)
            start = time.time()
            





    