
from pyfirmata2 import Arduino, PWM
import numpy as np

from scipy import signal
import iir_filter

PORT = Arduino.AUTODETECT

def define_filter_parameters(fs):
    filter_params = {
        'bandstop_filter': {
            'f0': 3.0,  # Lower cutoff frequency
            'f1': 6.0,  # Upper cutoff frequency
        },
        'lowpass_filter': {
            'f2': 10.0,  # Cutoff frequency
        },
        'sampling_rate': fs,
        'filter_order': 2  # Second-order filter
    }
    return filter_params

def initialize_iir_filters(filter_params):
    fs = filter_params['sampling_rate']
    f0, f1 = filter_params['bandstop_filter']['f0'], filter_params['bandstop_filter']['f1']
    f2 = filter_params['lowpass_filter']['f2']

    # Define the bandstop and lowpass filters (only first section for second order)
    sos1 = signal.butter(2, [f0/fs*2, f1/fs*2], 'bandstop', output='sos')[0]
    sos2 = signal.butter(2, f2/fs*2, 'lowpass', output='sos')[0]

    # Create instances of second-order IIR filters
    iir1 = iir_filter.IIR2_filter(sos1)
    iir2 = iir_filter.IIR2_filter(sos2)

    iir_filters = {
        'x_axis_filter': iir1,
        'y_axis_filter': iir2
    }

    print("Bandstop Filter Coefficients:", sos1)
    print("Lowpass Filter Coefficients:", sos2)
    return iir_filters

# Initialize your filter parameters and filters here
fs = 1000  # Example sampling rate, adjust based on your setup
filter_params = define_filter_parameters(fs)
iir_filters = initialize_iir_filters(filter_params)

def map_joystick_to_pwm(joystick_value, min_val=0, max_val=1023, min_pwm=0, max_pwm=255):
    # Ensure that the range is not zero to avoid division by zero
    if max_val - min_val == 0:
        raise ValueError("max_val and min_val must be different to avoid division by zero.")
        
    # Map the joystick value to a PWM value within the specified range
    normalized = (joystick_value - min_val) / (max_val - min_val)
    pwm_value = normalized * (max_pwm - min_pwm) + min_pwm
    
    # Clamp the pwm_value to the range [min_pwm, max_pwm] to avoid out-of-range values
    pwm_value = max(min_pwm, min(pwm_value, max_pwm))
    
    print(f"Joystick value: {joystick_value}, PWM value: {pwm_value}")
    return pwm_value

class PWMUpdater:
    def __init__(self, led_controller, rate_limit):
        self.led_controller = led_controller
        self.rate_limit = rate_limit
        self.last_pwm_x = 0
        self.last_pwm_y = 0

    def update_led1_color(self, joystick_x_value):
        new_pwm_value = map_joystick_to_pwm(joystick_x_value)
        # Apply rate limiting for a smooth transition
        if abs(new_pwm_value - self.last_pwm_x) > self.rate_limit:
            new_pwm_value = self.last_pwm_x + np.sign(new_pwm_value - self.last_pwm_x) * self.rate_limit
        self.led_controller.set_brightness('x', new_pwm_value)
        self.last_pwm_x = new_pwm_value
        print(f"Updated LED 1 brightness to {new_pwm_value}")

    def update_led2_color(self, joystick_y_value):
        new_pwm_value = map_joystick_to_pwm(joystick_y_value)
        # Apply rate limiting for a smooth transition
        if abs(new_pwm_value - self.last_pwm_y) > self.rate_limit:
            new_pwm_value = self.last_pwm_y + np.sign(new_pwm_value - self.last_pwm_y) * self.rate_limit
        self.led_controller.set_brightness('y', new_pwm_value)
        self.last_pwm_y = new_pwm_value
        print(f"Updated LED 2 brightness to {new_pwm_value}")

    
class JoystickDataCollector:
    def __init__(self, board, x_axis_pin_number, y_axis_pin_number, iir_filters):
        self.board = board
        self.x_axis_pin_number = x_axis_pin_number  # Pin number for X axis
        self.y_axis_pin_number = y_axis_pin_number  # Pin number for Y axis
        self.iir_filters = iir_filters

        self.x_axis_value = 0.0
        self.y_axis_value = 0.0

        # Setting up the callback for the joystick axes
        self.board.analog[x_axis_pin_number].register_callback(self.update_x_axis)
        self.board.analog[y_axis_pin_number].register_callback(self.update_y_axis)
        self.board.analog[x_axis_pin_number].enable_reporting()
        self.board.analog[y_axis_pin_number].enable_reporting()

    def update_x_axis(self, data):
        # Apply IIR filter to the joystick x-axis data
        self.x_axis_value = self.iir_filters['x_axis_filter'].filter(data)
        print(f"Filtered X-axis value: {self.x_axis_value}")

    def update_y_axis(self, data):
        # Apply IIR filter to the joystick y-axis data
        self.y_axis_value = self.iir_filters['y_axis_filter'].filter(data)
        print(f"Filtered Y-axis value: {self.y_axis_value}")

class LED_Controller:
    def __init__(self, board, led1_pin, led2_pin):
        self.board = board
        self.led1_pwm = self.board.get_pin(f'd:{led1_pin}:p')  # Digital pin for LED 1
        self.led2_pwm = self.board.get_pin(f'd:{led2_pin}:p')  # Digital pin for LED 2

        self.board.digital[led1_pin].mode = PWM
        self.board.digital[led2_pin].mode = PWM

    def set_brightness(self, axis, brightness):
        # Set LED brightness based on the axis and PWM value
        if axis == 'x':
            self.led1_pwm.write(brightness)
            print(f"Setting LED 1 (x-axis) to brightness {brightness}")
        elif axis == 'y':
            self.led2_pwm.write(brightness)
            print(f"Setting LED 2 (y-axis) to brightness {brightness}")
        else:
            raise ValueError(f"Invalid axis: {axis}")

def main():
    # Initialize the system
    board = Arduino(PORT)
    fs = 1000  # Example sampling rate
    filter_params = define_filter_parameters(fs)
    iir_filters = initialize_iir_filters(filter_params)

    # Initialize JoystickDataCollector and LED_Controller
    x_axis_pin, y_axis_pin = 0, 1
    led1_pin, led2_pin = 5, 6  # Pins for the two LEDs you're using
    #joystick_collector = JoystickDataCollector(board, x_axis_pin, y_axis_pin, iir_filters)
    joystick_collector = JoystickDataCollector(board, 0, 1, iir_filters)
    
    # Initialize LED_Controller with only two LEDs (red and green)
    led_controller = LED_Controller(board, led1_pin, led2_pin)

    # Initialize PWMUpdater
    pwm_updater = PWMUpdater(led_controller, rate_limit=0.05)
    print("Starting main loop...")
    
    # Main loop
    try:
        while True:
            x_value = joystick_collector.x_axis_value
            y_value = joystick_collector.y_axis_value
            pwm_updater.update_led1_color(x_value)
            pwm_updater.update_led2_color(y_value)
            
    except KeyboardInterrupt:
        print("KeyboardInterrupt has been caught.")
        board.exit()
        exit()
    except Exception as e:
        print(f"An error occurred outside the main loop: {e}")

if __name__ == '__main__':
    main()
