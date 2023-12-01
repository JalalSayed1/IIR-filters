from pyfirmata2 import Arduino, PWM
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

PORT = Arduino.AUTODETECT

# Define the pins
pin_x_axis = 0  # A0 for X axis
pin_y_axis = 1  # A1 for Y axis
led_red_pin = 5
led_blue_pin = 6
# led_brightness_pin = 5

# Establish a connection to the Arduino board
board = Arduino(PORT)

# Set the pins as PWM output
board.digital[led_red_pin].mode = PWM
board.digital[led_blue_pin].mode = PWM

# Function to map values
def map_value(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# Function to interpolate values
def interpolate(val, start_orig, end_orig, start_target, end_target):
    return ((val - start_orig) / (end_orig - start_orig)) * (end_target - start_target) + start_target

# Function to update LED brightness based on joystick values
def update_led_colour(pin_value):
    if pin_value < 0.01:
        print("## 1")
        duty_cycle_5 = 0.0
        duty_cycle_6 = 1.0
    elif pin_value > 0.99:
        print("## 2")
        duty_cycle_5 = 1.0
        duty_cycle_6 = 0.0
    else:
        # Smoothly transition both duty cycles based on pin_value
        duty_cycle_5 = interpolate(pin_value, 0, 1, 0, 1)
        duty_cycle_6 = 1 - duty_cycle_5

    board.digital[led_red_pin].write(duty_cycle_5)
    board.digital[led_blue_pin].write(duty_cycle_6)
    
    print(f"Red: {duty_cycle_5 * 100}% \t Blue: {duty_cycle_6 * 100}")

def update_led_brightness(pin_value):
    pwm_value = int(map_value(pin_value, 0, 1, 0, 100))
    board.digital[led_brightness_pin].write(pwm_value)
    print(f"Brightness: {pwm_value}%")
    

# Function to animate the LED brightness
# def animate(i):
#     update_led()

#' plotting
# Create lists to store data for plotting
time_vals = []
pin_vals = []

# Set up the plot
fig, ax = plt.subplots()
line, = ax.plot([], [], 'b-', label='Pin Value')
ax.set_xlim(0, 10)  # Set initial x-axis limits
ax.set_ylim(-0.5, 1.5)   # Set y-axis limits (adjust as needed)
ax.set_xlabel('Time')
ax.set_ylabel('Pin Value')
ax.legend()

# Function to update the plot data
def update_plot(frame):
    global time_vals, pin_vals

    # Read data from the pin (modify this according to your setup)
    pin_value = board.analog[pin_x_axis].read()

    # Append values to the lists
    current_time = time.time()
    time_vals.append(current_time)  # Use current time for x-axis
    pin_vals.append(pin_value)
    
    # Filter and limit the data to display in the plot
    time_window = 10  # Set the time window to display (adjust as needed)
    time_vals = [t for t in time_vals if current_time - t <= time_window]
    pin_vals = pin_vals[-len(time_vals):]

    # Update the plot with new data
    line.set_data(time_vals, pin_vals)

    # Update x-axis limits to display the most recent data
    if time_vals:
        ax.set_xlim(time_vals[0], time_vals[-1])

    return line,

# Function to initialize the plot
def init():
    line.set_data([], [])
    return line,

# Set up the animation
ani = animation.FuncAnimation(fig, update_plot, frames=np.linspace(0, 10, 100),
                              init_func=init, blit=True, interval=100)

#'------------

def callBack(pin, value):

    if pin == 0:
        print(f"pin: {pin} \t value: {value}")
        update_led_colour(value)
        
        
    # elif pin == 1:
        # update_led_brightness(value)
        # pass
    

sampling_rate = 200
board.samplingOn(1000 / sampling_rate)

# Set up animation
# ani = animation.FuncAnimation(plt.gcf(), animate, interval=50)

board.analog[pin_x_axis].register_callback(lambda value, pin=pin_x_axis: callBack(pin, value))
board.analog[pin_x_axis].enable_reporting()
board.analog[pin_y_axis].register_callback(lambda value, pin=pin_y_axis: callBack(pin, value))
board.analog[pin_y_axis].enable_reporting()

try:
    # Show the plot (this will not close automatically)
    plt.show()
    # while True:
    #     time.sleep(1)
    
except KeyboardInterrupt as e:
    print("KeyboardInterrupt")
    # print(e)

finally:
    print("Terminating program..")
    # Close the plot when Ctrl-C is pressed
    # plt.close()
    # Turn off the LED
    print("Turning off LED..")
    board.digital[led_blue_pin].write(0)
    board.digital[led_red_pin].write(0)
    # Close the serial connection to the Arduino board
    print("Closing serial connection to Arduino board..")
    board.exit()
    print("Program terminated")
    
    