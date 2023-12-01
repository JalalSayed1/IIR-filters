import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

#Credits Bernd Porr from https://github.com/berndporr/py-iir-filter
# Define the provided IIR2_filter and IIR_filter classes
class IIR2_filter:
    """2nd order IIR filter"""
    def __init__(self, s):
        """Instantiates a 2nd order IIR filter
        s -- numerator and denominator coefficients
        """
        self.numerator0 = s[0]
        self.numerator1 = s[1]
        self.numerator2 = s[2]
        self.denominator1 = s[4]
        self.denominator2 = s[5]
        self.buffer1 = 0
        self.buffer2 = 0

    def filter(self, v):
        """Sample by sample filtering
        v -- scalar sample
        returns filtered sample
        """
        input = v - (self.denominator1 * self.buffer1) - (self.denominator2 * self.buffer2)
        output = (self.numerator1 * self.buffer1) + (self.numerator2 * self.buffer2) + input * self.numerator0
        self.buffer2 = self.buffer1
        self.buffer1 = input
        return output

class IIR_filter:
    """IIR filter"""
    def __init__(self, sos):
        """Instantiates an IIR filter of any order
        sos -- array of 2nd order IIR filter coefficients
        """
        self.cascade = [IIR2_filter(s) for s in sos]

    def filter(self, data):
        """Sample by sample filtering
        data -- array of samples
        returns filtered samples
        """
        y = np.zeros_like(data)
        for i, v in enumerate(data):
            for f in self.cascade:
                v = f.filter(v)
            y[i] = v
        return y

# Define the bandstop and lowpass filter initialization functions
def initialize_bandstop_filter(fs, f0, f1, filter_order):
    """
    Initializes a bandstop filter with the given parameters.

    Parameters:
    fs (float): The sampling frequency.
    f0 (float): The lower cutoff frequency of the bandstop filter.
    f1 (float): The upper cutoff frequency of the bandstop filter.
    filter_order (int): The order of the filter.

    Returns:
    IIR_filter: The initialized bandstop filter.

    """
    sos = signal.butter(filter_order, [f0/fs*2, f1/fs*2], 'bandstop', output='sos')
    print("Bandstop Filter SOS Values:")
    for values in sos:
        print(values)
    return IIR_filter(sos)

def initialize_lowpass_filter(fs, f2, filter_order):
    sos = signal.butter(filter_order, f2/fs*2, 'lowpass', output='sos')
    print("Lowpass Filter SOS Values:")
    for values in sos:
        print(values)
    return IIR_filter(sos)

def initialize_bandpass_filter(fs, f3, f4, filter_order):
    sos = signal.butter(filter_order, [f3/fs*2, f4/fs*2], 'bandpass', output='sos')
    print("Bandpass Filter SOS Values:")
    for values in sos:
        print(values)
    return IIR_filter(sos)

# Generate a sample signal
fs = 1000  # Sampling rate
t = np.arange(0, 1.0, 1/fs)  # Time vector
sig = np.sin(2 * np.pi * 5 * t) + np.sin(2 * np.pi * 50 * t) + np.sin(2 * np.pi * 200 * t)

# Initialize filters
f0 = 120  # Bandstop lower cutoff
f1 = 140  # Bandstop upper cutoff
f2 = 100.0  # Lowpass cutoff
f3 = 120  # Bandpass lower cutoff
f4 = 140  # Bandpass upper cutoff
filter_order = 2

iir_bandstop = initialize_bandstop_filter(fs, f0, f1, filter_order)
iir_lowpass = initialize_lowpass_filter(fs, f2, filter_order)

# Apply filters
filtered_bandstop = iir_bandstop.filter(sig)
filtered_signal = iir_lowpass.filter(filtered_bandstop)

# Plot original and filtered signals
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(t, sig)
plt.title('Original Signal')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude')

plt.subplot(2, 1, 2)
plt.plot(t, filtered_signal)
plt.title('Filtered Signal')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude')

plt.tight_layout()
plt.show()
