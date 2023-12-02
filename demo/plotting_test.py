import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

sampling_rate = 200

#' plotting

buffer_size = 500

# Create figures and time domain
fig_time, ax_time = plt.subplots()
ax_time.set_xlabel('Time')
ax_time.set_ylabel('X-axis value')
ax_time.set_title('Time Domain')

# Create figures and frequency domain
fig_freq, ax_freq = plt.subplots()
ax_freq.set_xlabel('Frequency')
ax_freq.set_ylabel('Amplitude')
ax_freq.set_title('Frequency Domain')

# Initialize plot lines
time_domain_line, = ax_time.plot([], [], label='X-axis value (time domain)')
freq_domain_line, = ax_freq.plot([], [], label='X-axis value (frequency domain)')

# buffers:
time_domain_ring_buffer = []
time_domain_plot_data = np.zeros(buffer_size)
# freq_domain_plot_buffer = np.zeros(buffer_size)

# Function to update the plot data for both time and frequency domain
def update_time(frame):
    # global time_domain_plot_buffer, time_domain_ring_buffer, time_domain_line, buffer_size
    global time_domain_data, time_domain_line, buffer_size
    
    # update the time domain plot:
    if len(time_domain_data) >= buffer_size:
        time_domain_data = time_domain_data[-buffer_size:]
        time_domain_line.set_ydata(time_domain_data)
        # take the last "buffer_size" samples from the ring buffer:
        # time_domain_plot_buffer = np.append(time_domain_plot_buffer, time_domain_ring_buffer)[-buffer_size:]
        # empty the ring buffer as the old one will be plotted:
        # time_domain_ring_buffer.clear()
        # update the plot data:
        # time_domain_line.set_ydata(time_domain_plot_buffer)
        # time_domain_line.set_data(np.arange(len(time_domain_plot_buffer)), time_domain_plot_buffer)
    return time_domain_line,

def update_freq(frame):
    # global time_domain_plot_buffer, freq_domain_line, freq_domain_plot_buffer, buffer_size
    global time_domain_data, freq_domain_line, buffer_size
    # update the frequency domain plot:
    if len(time_domain_data) >= buffer_size:
        fft_data  = np.fft.fft(time_domain_data)
        fft_freq = np.fft.fftfreq(len(fft_data), 1 / sampling_rate)
        mask = fft_freq > 0
        freq_domain_line.set_data(fft_freq[mask], np.abs(fft_data[mask]))
        # freq_domain_plot_buffer = np.fft.fft(time_domain_plot_buffer)
        # fft_freq = np.fft.fftfreq(len(freq_domain_plot_buffer), 1 / sampling_rate)
        # remove the negative frequencies:
        # mask = fft_freq > 0
        # freq_domain_line.set_data(fft_freq[mask], np.abs(freq_domain_plot_buffer[mask]))
        
    
    return freq_domain_line,
    


# Function to initialize the plot
def init():
    time_domain_line.set_data([], [])
    freq_domain_line.set_data([], [])
    return time_domain_line, freq_domain_line

# Set up the animation
ani1 = animation.FuncAnimation(fig_time, update_time, frames=np.linspace(0, 10, 100), init_func=init, blit=True, interval=100)
ani2 = animation.FuncAnimation(fig_freq, update_freq, frames=np.linspace(0, 10, 100), init_func=init, blit=True, interval=100)

#'------------