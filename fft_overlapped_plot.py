#!/usr/bin/python3

from pyfirmata2 import Arduino
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Realtime oscilloscope at a sampling rate of 100Hz
# It displays analog channels 0 and 1 on the same plot.
# Now with frequency domain plotting for channel 0.

PORT = Arduino.AUTODETECT
# PORT = '/dev/ttyUSB0'

# Creates a scrolling data display
class RealtimePlotWindow:

    def __init__(self):
        # create a plot window for time domain
        self.fig_time, self.ax_time = plt.subplots()
        self.fig_time.suptitle('Time Domain')
        # that's our plotbuffer
        #* to be plotted:
        self.plotbuffer0 = np.zeros(500)
        self.plotbuffer1 = np.zeros(500)
        # create empty lines for each channel
        self.line0, = self.ax_time.plot(self.plotbuffer0, label='Analog 0')
        self.line1, = self.ax_time.plot(self.plotbuffer1, label='Analog 1')
        # axis
        self.ax_time.set_ylim(-0.5, 1.5)
        self.ax_time.legend()

        # create a plot window for frequency domain
        self.fig_freq, self.ax_freq = plt.subplots()
        self.fig_freq.suptitle('Frequency Domain')
        self.line_freq, = self.ax_freq.plot([], [], label='Frequency Spectrum')
        self.ax_freq.set_xlim(0, samplingRate / 2)
        self.ax_freq.set_xlabel('Frequency (Hz)')
        self.ax_freq.set_ylabel('Amplitude')
        self.ax_freq.legend()

        # That's our ringbuffer which accumulates the samples
        self.ringbuffer0 = []
        self.ringbuffer1 = []

        # start the animation
        self.ani_time = animation.FuncAnimation(self.fig_time, self.update_time, interval=100)
        self.ani_freq = animation.FuncAnimation(self.fig_freq, self.update_freq, interval=100)

    # updates the time domain plot
    def update_time(self, data):
        # add new data to the buffer
        self.plotbuffer0 = np.append(self.plotbuffer0, self.ringbuffer0)
        self.plotbuffer1 = np.append(self.plotbuffer1, self.ringbuffer1)
        # only keep the 500 newest ones and discard the old ones
        self.plotbuffer0 = self.plotbuffer0[-500:]
        self.plotbuffer1 = self.plotbuffer1[-500:]
        self.ringbuffer0 = []
        self.ringbuffer1 = []
        # set the new 500 points of the channels
        self.line0.set_ydata(self.plotbuffer0)
        self.line1.set_ydata(self.plotbuffer1)
        return self.line0, self.line1

    # updates the frequency domain plot
    def update_freq(self, data):
        fft_vals = np.fft.fft(self.plotbuffer0)
        fft_freq = np.fft.fftfreq(len(fft_vals), 1 / samplingRate)
        mask = fft_freq > 0
        self.line_freq.set_data(fft_freq[mask], np.abs(fft_vals[mask]))
        self.ax_freq.set_xlim(0, samplingRate / 2)
        self.ax_freq.set_ylim(0, max(np.abs(fft_vals[mask])) + 10)
        return self.line_freq,

    # appends data to the ringbuffer
    def addData(self, v, pin):
        if pin == 0:
            self.ringbuffer0.append(v)
        elif pin == 1:
            self.ringbuffer1.append(v)

# sampling rate: 100Hz
samplingRate = 500

# Create an instance of an animated scrolling window
realtimePlotWindow = RealtimePlotWindow()

# called for every new sample which has arrived from the Arduino
def callBack(pin, value):
    # pin will be the analog pin number, and value will be the sampled value
    realtimePlotWindow.addData(value, pin)

# Get the Arduino board.
board = Arduino(PORT)

# Set the sampling rate in the Arduino
board.samplingOn(1000 / samplingRate)

# Register the callback which adds the data to the animated plot
board.analog[0].register_callback(lambda value, pin=0: callBack(pin, value))
board.analog[0].enable_reporting()

board.analog[1].register_callback(lambda value, pin=1: callBack(pin, value))
board.analog[1].enable_reporting()

# show the plot and start the animation
plt.show()

# needs to be called to close the serial port
board.exit()

print("finished")
