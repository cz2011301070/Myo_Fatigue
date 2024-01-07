from CSVHandler import CSVHandler
import queue
import numpy as np
import mne
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import welch, hamming
# Generate a sample signal (replace this with your own signal)
fs = 200 
csvfilename = "zhuang.csv"
channel_name = ['C1','C2','C3','C4','C5','C6','C7','C8']
file = pd.read_csv(csvfilename)

EMGData = file.loc[:,channel_name[0]:channel_name[-1]]
EMGData = EMGData.values.tolist()

data = []

for i in range(len(channel_name)):
    data.append([float(row[i]) for row in EMGData])

signal = np.array(data)

signal = signal[0,:]

# Parameters for segmentation and windowing
nperseg = 100  # Number of samples per segment
overlap = nperseg // 2  # Overlapping samples (adjust as needed)
# Apply windowing to each segment (Hamming window in this example)
window = np.hamming(nperseg)
# Segment the signal and apply windowing
segments = []
for i in range(0, len(signal) - nperseg + 1, overlap):
    segment = signal[i:i+nperseg] * window
    segments.append(segment)

# Convert the list of segments to a numpy array
segments = np.array(segments)

# Compute FFT for each windowed segment
fft_result = np.fft.fft(segments, axis=-1)

# Calculate the corresponding frequencies
frequencies = np.fft.fftfreq(nperseg, 1/fs)




# Plot the original signal, the separated segments, and the FFT result
plt.figure(figsize=(12, 8))

plt.subplot(3, 1, 1)
plt.plot(signal)
plt.title('Original Signal')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')

plt.subplot(3, 1, 2)
plt.imshow(segments.T, aspect='auto', cmap='viridis', extent=[0, 5, 0, nperseg])
plt.title('Overlapping Segments')
plt.xlabel('Time (s)')
plt.ylabel('Segment Index')

plt.subplot(3, 1, 3)
plt.imshow(np.abs(fft_result), aspect='auto', cmap='viridis', extent=[0, 5, frequencies.min(), frequencies.max()])
plt.title('FFT Result')
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')

plt.tight_layout()
plt.show()

data = data * 1e-6
channel_types = ['emg' for _ in range(len(channel_name))]



info = mne.create_info(channel_name, fs, channel_types)

raw = mne.io.RawArray(data, info)
spectrum = raw.compute_psd(method='welch', picks=['emg'])
# spectrum.plot(picks=['C2'])
N = 50 # frequency window
r = 50 # time window, seconds
freqs = spectrum.freqs
psd = spectrum['C1'][0]


# get the N-1 psd values
for i in len(psd):
    (N-(i+1))* psd

# gama = np.sqrt((1/N-1)*np.sum(np.square(spectrum.psd)))

print()



