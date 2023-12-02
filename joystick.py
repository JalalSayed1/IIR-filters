from pyfirmata2 import Arduino, PWM
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from py_iir_filter.iir_filter import IIR_filter
from scipy.signal import butter, sosfreqz

# Constants
PORT = Arduino.AUTODETECT
BUFFER_SIZE = 500
SAMPLING_RATE = 200
LP_CUTOFF = 20

# Arduino Setup
board = Arduino(PORT)
board.samplingOn(1000 / SAMPLING_RATE)

# Define the pins
pin_x_axis = 0  # Analog pin A0 for X axis
led_red_pin = 5
led_blue_pin = 6

# Set the pins as PWM output
board.digital[led_red_pin].mode = PWM
board.digital[led_blue_pin].mode = PWM

# Function to update LED color based on joystick values
def update_led_color(pin_value):
    duty_cycle_red = interpolate(pin_value, 0, 1, 0, 1)
    duty_cycle_blue = 1 - duty_cycle_red

    board.digital[led_red_pin].write(duty_cycle_red)
    board.digital[led_blue_pin].write(duty_cycle_blue)

# Function to interpolate values
def interpolate(val, start_orig, end_orig, start_target, end_target):
    return ((val - start_orig) / (end_orig - start_orig)) * (end_target - start_target) + start_target

# Initialize Data Buffers
time_domain_data = np.zeros(BUFFER_SIZE)
fig, (ax_time, ax_freq) = None, (None, None)
line_time = None
line_freq = None

def setup_plotting(fig, ax_time, ax_freq, time_domain_data, line_time, line_freq):
    # Initialize Figures
    fig, (ax_time, ax_freq) = plt.subplots(2, 1,)

    # Time Domain Plot
    ax_time.set_xlabel('Time')
    ax_time.set_ylabel('X-axis Value')
    ax_time.set_title('Time Domain')
    ax_time.set_ylim(-0.1, 1.1)
    line_time, = ax_time.plot(np.arange(BUFFER_SIZE), time_domain_data, label='X-axis value')

    # Frequency Domain Plot
    ax_freq.set_xlabel('Frequency')
    ax_freq.set_ylabel('Amplitude')
    ax_freq.set_title('Frequency Domain')
    line_freq, = ax_freq.plot([], [], label='X-axis Value (Frequency Domain)')
    ax_freq.set_xlim(0, SAMPLING_RATE / 2)
    ax_freq.set_ylim(0, 50)
    ax_freq.set_xticks(np.arange(0, SAMPLING_RATE/2 + 1, 10))
    
    return fig, (ax_time, ax_freq), time_domain_data, line_time, line_freq

# Function to Update Plots
def update_plot(frame):
    global time_domain_data

    # Update Time Domain Data
    new_data = board.analog[pin_x_axis].read()  # Read new data from Arduino
    if new_data is not None:
        time_domain_data = np.roll(time_domain_data, -1)
        time_domain_data[-1] = new_data
        line_time.set_ydata(time_domain_data)

        # Update Frequency Domain Data
        fft_data = np.fft.fft(time_domain_data)
        fft_freq = np.fft.fftfreq(BUFFER_SIZE, 1 / SAMPLING_RATE)
        mask = fft_freq > 0
        line_freq.set_data(fft_freq[mask], np.abs(fft_data[mask]))

    return line_time, line_freq

# Function to Initialize the Plot
def init():
    line_time.set_ydata(np.zeros(BUFFER_SIZE))
    line_freq.set_data([], [])
    return line_time, line_freq

# Arduino Callback for LED Update
def joystick_callback(value):
    update_led_color(value)

try:
    fig, (ax_time, ax_freq), time_domain_data, line_time, line_freq = setup_plotting(fig, ax_time, ax_freq, time_domain_data, line_time, line_freq)
    # Create Animation
    ani = animation.FuncAnimation(fig, update_plot, init_func=init, blit=True, interval=1)
    board.analog[pin_x_axis].register_callback(joystick_callback)
    board.analog[pin_x_axis].enable_reporting()

    # Show Plot
    plt.tight_layout()
    plt.show()
    
except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    # Cleanup
    board.digital[led_blue_pin].write(0)
    board.digital[led_red_pin].write(0)
    board.exit()
    print("Program terminated")
