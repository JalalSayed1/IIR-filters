#!/usr/bin/python3

from pyfirmata2 import Arduino
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Realtime oscilloscope at a sampling rate of 100Hz
# It displays analog channels 0 and 1 on the same plot.
# Copyright (c) 2018-2020, Bernd Porr <mail@berndporr.me.uk>
# see LICENSE file.

PORT = Arduino.AUTODETECT
# PORT = '/dev/ttyUSB0'

# Creates a scrolling data display
class RealtimePlotWindow:

    def __init__(self):
        # create a plot window
        self.fig, self.ax = plt.subplots()
        # that's our plotbuffer
        self.plotbuffer0 = np.zeros(500)
        self.plotbuffer1 = np.zeros(500)
        # create empty lines for each channel
        self.line0, = self.ax.plot(self.plotbuffer0, label='Analog Pin 0')
        self.line1, = self.ax.plot(self.plotbuffer1, label='Analog Pin 1')
        # axis
        self.ax.set_ylim(0, 1.5)
        # That's our ringbuffer which accumulates the samples
        # It's emptied every time when the plot window below
        # does a repaint
        self.ringbuffer0 = []
        self.ringbuffer1 = []
        # add any initialization code here (filters etc)
        # start the animation
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=100)
        # add a legend to the plot
        self.ax.legend()

    # updates the plot
    def update(self, data):
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

    # appends data to the ringbuffer
    def addData(self, v, pin):
        if pin == 0:
            self.ringbuffer0.append(v)
        elif pin == 1:
            self.ringbuffer1.append(v)


# Create an instance of an animated scrolling window
realtimePlotWindow = RealtimePlotWindow()

# sampling rate: 100Hz
samplingRate = 100

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
board.analog[1].register_callback(lambda value, pin=1: callBack(pin, value))

# Enable the callbacks
board.analog[0].enable_reporting()
board.analog[1].enable_reporting()

# show the plot and start the animation
plt.show()

# needs to be called to close the serial port
board.exit()

print("finished")
