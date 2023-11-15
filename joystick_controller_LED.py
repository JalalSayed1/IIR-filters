#!/usr/bin/python3

from pyfirmata2 import Arduino
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

PORT = Arduino.AUTODETECT
# PORT = '/dev/ttyACM0'

class LEDController:

    def __init__(self):
        # sampling rate: 10Hz
        self.samplingRate = 10
        self.board = Arduino(PORT)
        self.x_axis = [0]
        self.y_axis = [0]
        self.switch = [0]
        self.x_axis_pin, self.y_axis_pin, self.sw_pin = self.setup()

        self.setup_plotting()
        
        #! add any initialization code here (filters etc)?
        
        

        
        

    '''
    No need to call this function. It is called automatically when the object is created. 
    '''
    def setup(self):
        # x axis:
        self.board.samplingOn(1000 / self.samplingRate)
        x_axis_pin = self.board.get_pin('a:0:i')
        x_axis_pin.enable_reporting()
        x_axis_pin.register_callback(lambda value, pin=0: self.add_new_data(value, pin))
        # y axis:
        y_axis_pin = self.board.get_pin('a:1:i')
        y_axis_pin.enable_reporting()
        y_axis_pin.register_callback(lambda value, pin=1: self.add_new_data(value, pin))
        # switch:
        sw_pin = self.board.get_pin('d:7:i')
        sw_pin.enable_reporting()
        sw_pin.register_callback(lambda value, pin=7: self.add_new_data(value, pin))
        
        return x_axis_pin, y_axis_pin, sw_pin
    
    
    def setup_plotting(self):
        # plotting window:
        self.fig, self.ax = plt.subplots()
        # buffers for data:
        self.plot_buffer_x_axis = np.zeros(500)
        self.plot_buffer_y_axis = np.zeros(500)
        self.plot_buffer_sw = np.zeros(500)
        # create empty lines:
        self.line_x_axis, = self.ax.plot(self.plot_buffer_x_axis, label='X axis')
        self.line_y_axis, = self.ax.plot(self.plot_buffer_y_axis, label='Y axis')
        self.line_sw, = self.ax.plot(self.plot_buffer_sw, label='Switch')
        
        self.ax.set_ylim(-0.5, 1.5)
        
        # ring buffers to accumulate samples. It's emptied every time when the plot window below does a repaint:
        self.ring_buffer_x_axis = []
        self.ring_buffer_y_axis = []
        self.ring_buffer_sw = []
        
        #! add any initialization code here (filters etc)
        
        # start the animation
        self.ani = animation.FuncAnimation(self.fig, self.update_plot, interval=100)
        
        self.ax.legend()
        #! might need to change this:
        # plt.show()
        
    
    def read_sensor_data(self):
        # append latest data from the sensor:
        self.x_axis.append(self.x_axis_pin.read())
        self.y_axis.append(self.y_axis_pin.read())
        self.switch.append(self.sw_pin.read())
        
        return self.x_axis, self.y_axis, self.switch
        
    def read_and_print(self):
        self.read_sensor_data()
        # print latest data from the sensor only:
        print(f"x_axis: {self.x_axis[-1]}, y_axis: {self.y_axis[-1]}, switch: {self.switch[-1]}")
        # self.update_plot()
        
    
    def update_plot(self, frame):
        # append values to buffers:
        # same args to append to itself.
        self.plot_buffer_x_axis = np.append(self.plot_buffer_x_axis, self.ring_buffer_x_axis)
        self.plot_buffer_y_axis = np.append(self.plot_buffer_y_axis, self.ring_buffer_y_axis)
        self.plot_buffer_sw = np.append(self.plot_buffer_sw, self.ring_buffer_sw)
        # only keep the 500 newest ones and discard the old ones:
        self.plot_buffer_x_axis = self.plot_buffer_x_axis[-500:]
        self.plot_buffer_y_axis = self.plot_buffer_y_axis[-500:]
        self.plot_buffer_sw = self.plot_buffer_sw[-500:]
        
        # empty ring buffers:
        self.ring_buffer_x_axis = []
        self.ring_buffer_y_axis = []
        self.ring_buffer_sw = []
        
        # set the new 500 points of the channels:
        self.line_x_axis.set_ydata(self.plot_buffer_x_axis)
        self.line_y_axis.set_ydata(self.plot_buffer_y_axis)
        self.line_sw.set_ydata(self.plot_buffer_sw)
        
        return self.line_x_axis, self.line_y_axis, self.line_sw
        
        
    def add_new_data(self, v, pin):
        if pin == 0:
            self.ring_buffer_x_axis.append(v)
        elif pin == 1:
            self.ring_buffer_y_axis.append(v)
        elif pin == 7:
            self.ring_buffer_sw.append(v)

    def stop(self):
        self.board.samplingOff()
        self.board.exit()
        # if self.ani:
        #     plt.close(self.fig)


print("Starting...")

LED_controller = LEDController()
# LED_controller.start_plotting()

# input("Start?")
try:
    while True:
        LED_controller.read_and_print()
        # plt.show()
        time.sleep(0.3)
        # plt.pause(0.1)
        
except KeyboardInterrupt:
    LED_controller.stop()
    print("Finished 👍")

plt.show()
