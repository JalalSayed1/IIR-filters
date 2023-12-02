# Arduino Joystick Data Visualization

This Python script visualizes joystick data from an Arduino board using PyFirmata, Matplotlib, and Py-IIR-Filter.

## Requirements

- Python 3.x
- PyFirmata 2.x
- Matplotlib
- NumPy

Install the required Python packages using pip:

```bash
pip install pyfirmata matplotlib numpy
```

## Usage

1. Connect your Arduino board to your computer.
2. Connect a joystick to your Arduino board.
   - Connect the X-axis to analog pin A0.
   - Connect the power and GND pins to the board's 5V and GND pins.
3. Connect two RB LED's to your Arduino board.
   - Connect the red pin on one of the LED's to digital pin 5.
   - Connect the blue pin of this LED to digital pin 6.
   - Connect the other RB LED to the same pins but swap the red and blue pins (to make a switching effect).
   - Connect both GND pins to the board's GND.
   - No resistors are needed.
4. Run `main.py` script:

    ```bash
    python main.py
    ```

    The script will start visualizing the joystick data on a Matplotlib graph in real-time.

## Video demo

[![Video demo](https://img.youtube.com/vi/2Z3Z4Z3Z4Z4/0.jpg)](https://www.youtube.com/watch?v=2Z3Z4Z3Z4Z4)
