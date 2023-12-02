import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Function to generate data
fft_data = np.zeros(128)
def generate_data(t):
    signal1 = 0.5 * np.sin(2 * np.pi * 2 * t) + 0.3 * np.cos(2 * np.pi * 5 * t) + 0.2 * np.sin(2 * np.pi * 10 * t)
    
    global fft_data
    fft_data = np.append(fft_data, signal1)[-128:]
    
    signal2 = np.fft.fft(fft_data)
    return signal1, signal2

# Initialize the figure and axes for two subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
xdata, ydata1 = [], []
ln1, = ax1.plot([], [], 'r-', animated=True)
ln2, = ax2.plot([], [], 'b-', animated=True)

# Set the axis limits for both subplots
ax1.set_xlim(0, 2)
ax1.set_ylim(-1, 1)
ax2.set_xlim(0, len(fft_data)//2)
ax2.set_ylim(0, 50)  # Adjust the y-axis limits for the FFT plot

# Initialize the data lists with zeros
initial_frame = 0
xdata.append(initial_frame)
ydata1.append(0)

# Function to initialize the plots
def init():
    ln1.set_data([], [])
    ln2.set_data([], [])
    return ln1, ln2

# Function to update the plots in real-time
def update(frame):
    xdata.append(frame)
    signal1, signal2 = generate_data(frame)
    ydata1.append(signal1)

    # Update only the magnitude spectrum of the FFT for a specific frequency bin
    fft_magnitude = np.abs(signal2)[:len(fft_data)//2]
    ln1.set_data(xdata[-128:], ydata1[-128:])
    ln2.set_data(np.arange(len(fft_magnitude)), fft_magnitude)
    
    return ln1, ln2

# Create an animation
ani = animation.FuncAnimation(fig, update, frames=np.linspace(0, 2, 128),
                              init_func=init, blit=True)

plt.tight_layout()
plt.show()
