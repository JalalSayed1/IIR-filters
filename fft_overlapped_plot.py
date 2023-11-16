#!/usr/bin/python3

from pyfirmata2 import Arduino
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Realtime oscilloscope at a sampling rate of 100Hz
# It displays analog channels 0 and 1 on the same plot in both time and frequency domains.

PORT = Arduino.AUTODETECT
# PORT = '/dev/ttyUSB0'

# Creates a scrolling data display
class RealtimePlotWindow:

    def __init__(self):
        # Create a plot window for time domain
        self.fig_time, self.ax_time = plt.subplots()
        self.fig_time.suptitle('Time Domain')
        # Plot buffers for channels 0 and 1
        self.plotbuffer0 = np.zeros(500)
        self.plotbuffer1 = np.zeros(500)
        # Create empty lines for each channel
        self.line0, = self.ax_time.plot(self.plotbuffer0, label='Analog 0')
        self.line1, = self.ax_time.plot(self.plotbuffer1, label='Analog 1')
        # Axis settings
        self.ax_time.set_ylim(-0.5, 1.5)
        self.ax_time.legend()

        # Create a plot window for frequency domain
        self.fig_freq, self.ax_freq = plt.subplots()
        self.fig_freq.suptitle('Frequency Domain')
        self.line_freq0, = self.ax_freq.plot([], [], label='Frequency Spectrum - A0')
        self.line_freq1, = self.ax_freq.plot([], [], label='Frequency Spectrum - A1')
        self.ax_freq.set_xlabel('Frequency (Hz)')
        self.ax_freq.set_ylabel('Amplitude')
        self.ax_freq.legend()

        # Ringbuffers for accumulating samples
        self.ringbuffer0 = []
        self.ringbuffer1 = []

        # Start the animation
        self.ani_time = animation.FuncAnimation(self.fig_time, self.update_time, interval=100)
        self.ani_freq = animation.FuncAnimation(self.fig_freq, self.update_freq, interval=100)

    def update_time(self, data):
        # Add new data to the buffers and update plots
        self.plotbuffer0 = np.append(self.plotbuffer0, self.ringbuffer0)[-500:]
        self.plotbuffer1 = np.append(self.plotbuffer1, self.ringbuffer1)[-500:]
        self.ringbuffer0 = []
        self.ringbuffer1 = []
        self.line0.set_ydata(self.plotbuffer0)
        self.line1.set_ydata(self.plotbuffer1)
        return self.line0, self.line1

    def update_freq(self, data):
        # Update frequency domain plot for both channels
        fft_vals0 = np.fft.fft(self.plotbuffer0)
        fft_vals1 = np.fft.fft(self.plotbuffer1)
        fft_freq = np.fft.fftfreq(len(fft_vals0), 1 / samplingRate)
        mask = fft_freq > 0

        self.line_freq0.set_data(fft_freq[mask], np.abs(fft_vals0[mask]))
        self.line_freq1.set_data(fft_freq[mask], np.abs(fft_vals1[mask]))
        self.ax_freq.set_xlim(0, samplingRate / 2)
        max_amplitude = max(max(np.abs(fft_vals0[mask])), max(np.abs(fft_vals1[mask]))) + 10
        self.ax_freq.set_ylim(0, max_amplitude)

        return self.line_freq0, self.line_freq1

    def addData(self, v, pin):
        # Append data to the appropriate ringbuffer
        if pin == 0:
            self.ringbuffer0.append(v)
        elif pin == 1:
            self.ringbuffer1.append(v)

# Sampling rate: 100Hz
samplingRate = 500

# Create an instance of the animated scrolling window
realtimePlotWindow = RealtimePlotWindow()

def callBack(pin, value):
    realtimePlotWindow.print_values(pin, value)
    # Callback for new samples from the Arduino
    realtimePlotWindow.addData(value, pin)

# Get the Arduino board
board = Arduino(PORT)

# Set the sampling rate in the Arduino
board.samplingOn(1000 / samplingRate)

#' pin assignments:
x_axis_pin = 0 # A0
y_axis_pin = 1 # A1
sw_pin = 7 # D7
# pwm_pin = 6 # D6

# Register callbacks for both analog pins
board.analog[x_axis_pin].register_callback(lambda value, pin=x_axis_pin: callBack(pin, value))
board.analog[x_axis_pin].enable_reporting()
board.analog[y_axis_pin].register_callback(lambda value, pin=y_axis_pin: callBack(pin, value))
board.analog[y_axis_pin].enable_reporting()

# pwm signal from digital pin 8:
# pwm = board.get_pin(f'd:{pwm_pin}:p')



# Show the plot and start the animation
plt.show()

# pwm.write(0)
# Close the serial port
board.exit()

print("Finished 👍")
