from pyfirmata2 import Arduino, util, SERVO
import time

# Specify the port where your Arduino is connected
# port = '/dev/ttyACM0'  # Replace with the correct port

PORT = Arduino.AUTODETECT
board = Arduino(PORT)

# Attach a servo to a pin
pin = 9  # PWM pin where the servo is connected
board.digital[pin].mode = SERVO

def rotate_servo(pin, angle):
    """Rotates the servo to the specified angle."""
    board.digital[pin].write(angle)
    time.sleep(0.015)

try:
    # while True:
        # Example: Rotate servo between 0 and 180 degrees
    for angle in range(0, 181, 1):
        rotate_servo(pin, angle)
            # time.sleep(0.01)
        # for angle in range(180, -1, -1):
        #     rotate_servo(pin, angle)
        #     # time.sleep(0.01)
    
    rotate_servo(pin, 90)
    # time.sleep(0.01)
    # rotate_servo(pin, 180)
    # time.sleep(0.01)

except KeyboardInterrupt:
    # Turn off servo on Ctrl+C
    rotate_servo(pin, 0)
    board.exit()


# pin = 9  # PWM pin where the servo is connected
# board.digital[pin].mode = SERVO

# rotate_servo(pin, 0)
