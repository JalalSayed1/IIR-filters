#!/usr/bin/python3

from pyfirmata2 import Arduino
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

PORT = Arduino.AUTODETECT
# PORT = '/dev/ttyACM0'

class LEDController:

    def __init__(self):
        # sampling rate: 10Hz
        self.samplingRate = 10
        self.timestamp = 0
        self.board = Arduino(PORT)
        self.x_axis = [0]
        self.y_axis = [0]
        self.switch = [0]
        self.fig, self.ax = plt.subplots()
        self.ani = None
        self.x_axis_pin, self.y_axis_pin, self.sw_pin = self.setup()
        

    '''
    No need to call this function. It is called automatically when the object is created. 
    '''
    def setup(self):
        # self.board.analog[0].register_callback(self.myPrintCallback)
        self.board.samplingOn(1000 / self.samplingRate)
        # self.board.analog[0].enable_reporting() # x axis
        x_axis_pin = self.board.get_pin('a:0:i')
        x_axis_pin.enable_reporting()
        # self.board.analog[1].enable_reporting() # y axis
        y_axis_pin = self.board.get_pin('a:1:i')
        y_axis_pin.enable_reporting()
        sw_pin = self.board.get_pin('d:7:i') # switch
        sw_pin.enable_reporting()
        
        return x_axis_pin, y_axis_pin, sw_pin
    
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
        
    
    # def start_plotting(self):
    #     self.ani = FuncAnimation(self.fig, self.update_plot, interval=100)
    #     self.ax.set_title('Real-time Sensor Data')
    #     self.ax.set_xlabel('Time')
    #     self.ax.set_ylabel('Sensor Values')
    #     plt.pause(0.1)  # Displaying the plot window for a short duration

    # def update_plot(self, frame=None):
    #     self.ax.clear()
    #     self.ax.plot(range(len(self.x_axis)), self.x_axis, label='X Axis')
    #     self.ax.plot(range(len(self.y_axis)), self.y_axis, label='Y Axis')
    #     self.ax.plot(range(len(self.switch)), self.switch, label='Switch')
    #     self.ax.legend()
    #     self.ax.set_title('Real-time Sensor Data')
    #     self.ax.set_xlabel('Time')
    #     self.ax.set_ylabel('Sensor Values')


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
        time.sleep(0.3)

except KeyboardInterrupt:
    LED_controller.stop()
    print("Finished 👍")
