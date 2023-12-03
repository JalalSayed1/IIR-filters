from pyfirmata2 import Arduino, PWM
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from py_iir_filter.iir_filter import IIR_filter
from scipy.signal import butter
import tkinter as tk

# ' Constants
X_AXIS_INPUT = 0  # Analog pin A0 for X axis
LED_RED_PIN = 5  # Digital pin D5 for red LED
LED_BLUE_PIN = 6  # Digital pin D6 for blue LED

PORT = Arduino.AUTODETECT
BUFFER_SIZE = 300  # samples
SAMPLING_RATE = 200  # Hz
print(f"Sampling rate: {SAMPLING_RATE} Hz")

# Plotting figure size:
WIDTH = 15  # inches
HEIGHT = WIDTH * (9 / 16)  # 16:9 aspect ratio

# ' Arduino Setup
board = Arduino(PORT)
board.samplingOn(1000 / SAMPLING_RATE)

# ' Set the pins as PWM output
board.digital[LED_RED_PIN].mode = PWM
board.digital[LED_BLUE_PIN].mode = PWM

# ' IIR filter:
LP_CUTOFF = 10  # Hz
NYQUIST_RATE = SAMPLING_RATE / 2
sos = butter(2, LP_CUTOFF / NYQUIST_RATE, btype='low', output='sos')
iir_filter = IIR_filter(sos)

# ' Plotting:
# initialized to none so they will be created in setup_plotting()
fig, (ax_time, ax_freq) = None, (None, None)
line_time = None
filtered_line_time = None
line_freq = None
filtered_line_freq = None
time_domain_data = np.zeros(BUFFER_SIZE)
filtered_time_domain_data = np.zeros(BUFFER_SIZE)
freq_domain_data = np.zeros(BUFFER_SIZE // 2)
filtered_freq_domain_data = np.zeros(BUFFER_SIZE // 2)

# current sample from pin:
current_sample = 0.0

# Make a button to toggle between using filtered data or not in real time:
use_filtered_data = False
status_text = None


# Use the filtered data to update the LED or raw data (True or False):
def toggle_filtered_data():
    global use_filtered_data, status_text
    use_filtered_data = not use_filtered_data
    text = "Using filtered data to update LED.." if use_filtered_data else "NOT using filtered data to update LED.."
    print(text)
    status_text.config(text=text)


# Create a function to setup the GUI elements
def setup_gui():
    global use_filtered_data, status_text
    root = tk.Tk()
    root.title("Toggle Filtered Data")

    # Set the initial size of the window (width x height)
    window_width = 300
    window_height = 80
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (window_width / 2)
    y_coordinate = (screen_height / 2) - (window_height / 2)
    root.geometry("%dx%d+%d+%d" %
                  (window_width, window_height, x_coordinate, y_coordinate))

    # Create" a button to toggle filtered data
    toggle_button = tk.Button(
        root, text="Toggle LED response", command=toggle_filtered_data)

    text = "Using filtered data to update LED.." if use_filtered_data else "NOT using filtered data to update LED.."
    status_text = tk.Label(root, text=text)

    status_text.pack()
    toggle_button.pack()

    return root


# Function to update LED color based on joystick values
def update_led_color(pin_value):
    # pin_value is already between 0 and 1:
    duty_cycle_red = pin_value
    duty_cycle_blue = 1 - duty_cycle_red

    board.digital[LED_RED_PIN].write(duty_cycle_red)
    board.digital[LED_BLUE_PIN].write(duty_cycle_blue)


def setup_plotting(fig, ax_time, ax_freq, time_domain_data, line_time, line_freq, filtered_time_domain_data, filtered_line_time):
    # Initialize Figures
    fig, (ax_time, ax_freq) = plt.subplots(2, 1, figsize=(WIDTH, HEIGHT))

    # Time Domain Plot
    ax_time.set_xlabel('Time')
    ax_time.set_ylabel('X-axis Value')
    ax_time.set_title('Time Domain')
    ax_time.set_ylim(-0.1, 1.1)
    line_time, = ax_time.plot(np.arange(BUFFER_SIZE),
                              time_domain_data, label='X-axis value')
    filtered_line_time, = ax_time.plot(np.arange(
        BUFFER_SIZE), filtered_time_domain_data, label='Filtered X-axis value')
    ax_time.legend()  # Add legend for time domain plot

    # Frequency Domain Plot
    ax_freq.set_xlabel('Frequency')
    ax_freq.set_ylabel('Amplitude')
    ax_freq.set_title('Frequency Domain')
    ax_freq.set_xlim(0, SAMPLING_RATE / 2)
    ax_freq.set_ylim(0, 50)
    line_freq, = ax_freq.plot([], [], label='X-axis value')
    filtered_line_freq, = ax_freq.plot([], [], label='Filtered X-axis value')
    ax_freq.legend()  # Add legend for frequency domain plot

    return fig, (ax_time, ax_freq), time_domain_data, line_time, line_freq, filtered_time_domain_data, filtered_line_time, filtered_line_freq


# Function to Update Plots
def update(frame):
    global time_domain_data, filtered_time_domain_data, current_sample, use_filtered_data

    if current_sample is not None:
        # Update Time Domain Data
        # store raw data:
        time_domain_data = np.roll(time_domain_data, -1)
        time_domain_data[-1] = current_sample

        # Apply filter:
        filtered_data = iir_filter.filter(current_sample)
        filtered_time_domain_data = np.roll(filtered_time_domain_data, -1)
        filtered_time_domain_data[-1] = filtered_data

        # plot time domain data:
        line_time.set_ydata(time_domain_data)
        filtered_line_time.set_ydata(filtered_time_domain_data)

        # Update Frequency Domain Data
        fft_data = np.fft.fft(time_domain_data)
        filtered_fft_data = np.fft.fft(filtered_time_domain_data)
        # get the frequency bins:
        fft_freq = np.fft.fftfreq(BUFFER_SIZE, 1 / SAMPLING_RATE)

        # plot the data:
        mask = fft_freq > 0  # Only plot the positive frequencies
        line_freq.set_data(fft_freq[mask], np.abs(fft_data[mask]))
        filtered_line_freq.set_data(
            fft_freq[mask], np.abs(filtered_fft_data[mask]))

    # Update LED
    if use_filtered_data:
        # max value for filtered data is 1 and min is 0. Check that is true:
        filtered_data = np.clip(filtered_data, 0, 1)
        print(f"Filtered data: {filtered_data}")
        update_led_color(filtered_data)
    else:
        print(f"Raw data: {current_sample}")
        update_led_color(current_sample)

    return line_time, line_freq, filtered_line_time, filtered_line_freq


# Function to Initialize the Plot
def init():
    line_time.set_ydata(np.zeros(BUFFER_SIZE))
    filtered_line_time.set_ydata(np.zeros(BUFFER_SIZE))
    line_freq.set_data([], [])
    filtered_line_freq.set_data([], [])
    return line_time, line_freq, filtered_line_time, filtered_line_freq


# Arduino Callback for LED Update
def callback(value):
    global current_sample
    current_sample = value


# Setup everything related to plotting:
fig, (ax_time, ax_freq), time_domain_data, line_time, line_freq, filtered_time_domain_data, filtered_line_time, filtered_line_freq = setup_plotting(
    fig, ax_time, ax_freq, time_domain_data, line_time, line_freq, filtered_time_domain_data, filtered_line_time)

# Create Animation
ani = animation.FuncAnimation(
    fig, update, init_func=init, blit=True, interval=1)

board.analog[X_AXIS_INPUT].register_callback(callback)
board.analog[X_AXIS_INPUT].enable_reporting()

try:
    root = setup_gui()
    plt.tight_layout()
    plt.show()

except KeyboardInterrupt:
    print("Interrupted by user")

finally:
    # Cleanup:
    board.digital[LED_BLUE_PIN].write(0)
    board.digital[LED_RED_PIN].write(0)
    board.exit()
    print("Program terminated")
