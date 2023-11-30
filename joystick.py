from pyfirmata2 import Arduino, PWM
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

PORT = Arduino.AUTODETECT

'''
Get values of the joystick x and y axis on pin A0 and A1. Output PWM signal that corresponds to the values on pin D6 and D7 respectively which are connected to the R and G pins of Green & Red LED.'''


# Define the pins
pin_x_axis = 0  # A0 for X axis
pin_y_axis = 1  # A1 for Y axis
pin_red_led = 5  # D5 for Red LED
pin_green_led = 6  # D6 for Green LED

# Establish a connection to the Arduino board
board = Arduino(PORT)

# Set the pins as PWM output
board.digital[pin_red_led].mode = PWM
board.digital[pin_green_led].mode = PWM

# Function to map values
def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Function to update LED brightness based on joystick values
def update_led():
    x_value = board.analog[pin_x_axis].read()  # Read X axis value
    y_value = board.analog[pin_y_axis].read()  # Read Y axis value
    
    print(f"x_value: {x_value} \t y_value: {y_value}")

    if x_value is not None and y_value is not None:
        # Map the joystick values to PWM range (0-255)
        # pwm_x = int(map_value(x_value, 0, 1, 0, 255))
        # pwm_y = int(map_value(y_value, 0, 1, 0, 255))
        pwm_x = int(map_value(x_value, 0, 1, 1, 100))
        pwm_y = int(map_value(y_value, 0, 1, 1, 100))

        # Update the LED brightness
        board.digital[pin_red_led].write(pwm_x)
        board.digital[pin_green_led].write(pwm_y)

# Function to animate the LED brightness
def animate(i):
    update_led()
    
def callBack(pin, value):
    update_led()
    

sampling_rate = 200
board.samplingOn(1000 / sampling_rate)

# Set up animation
ani = animation.FuncAnimation(plt.gcf(), animate, interval=50)

board.analog[pin_x_axis].register_callback(lambda value, pin=pin_x_axis: callBack(pin, value))
board.analog[pin_x_axis].enable_reporting()
board.analog[pin_y_axis].register_callback(lambda value, pin=pin_y_axis: callBack(pin, value))
board.analog[pin_y_axis].enable_reporting()

try:
    # Show the plot (this will not close automatically)
    plt.show()
    
except KeyboardInterrupt as e:
    print("KeyboardInterrupt")
    # print(e)

finally:
    print("Terminating program")
    # Close the plot when Ctrl-C is pressed
    # plt.close()
    # Turn off the LED
    board.digital[pin_red_led].write(0)
    board.digital[pin_green_led].write(0)
    # Close the serial connection to the Arduino board
    board.exit()
    
    