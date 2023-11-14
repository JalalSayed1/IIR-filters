import pyfirmata2
import time

# Adjust the port according to your system
PORT = pyfirmata2.Arduino.AUTODETECT

def get_distance(trig_pin, echo_pin):
    trig_pin.write(0)  # Set Trig pin low
    time.sleep(0.01)  # Short delay before trigger
    trig_pin.write(1)  # Send trigger pulse
    time.sleep(0.00001)  # Ensure the pulse is at least 10µs
    trig_pin.write(0)  # Turn off trigger signal

    timeout = time.time() + 0.1  # 100ms timeout
    while echo_pin.read() == 0 and time.time() < timeout:
        pass
    pulse_start = time.time()

    timeout = time.time() + 0.1  # 100ms timeout
    while echo_pin.read() == 1 and time.time() < timeout:
        pass
    pulse_end = time.time()

    duration = pulse_end - pulse_start
    speed_of_sound = 34300  # Speed of sound in cm/s at room temperature
    distance = (duration * speed_of_sound) / 2  # Calculate distance in cm
    
    if 2 <= distance <= 400:  # Limit measurements between 2cm and 400cm (or adjust as needed)
        return distance
    else:
        return None  # Discard invalid measurements

# Creates a new board
board = pyfirmata2.Arduino(PORT)
print("Setting up the connection to the board ...")

board.samplingOn(1)

echo_pin = board.get_pin('d:2:i')  # Assuming echo connected to digital pin 2
echo_pin.enable_reporting()

trig_pin = board.get_pin('d:3:o')  # Assuming trigger connected to digital pin 3

while True:
    distance = get_distance(trig_pin, echo_pin)
    if distance is not None:
        print(f"\nDistance: {distance:.4f} cm")
    time.sleep(0.5)
