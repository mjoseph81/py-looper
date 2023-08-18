import pyaudio
import matplotlib.pyplot as plt
import numpy as np
import wave
import sys
import time

pa = pyaudio.PyAudio()

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
INDEVICE = 5
OUTDEVICE = 5
CHUNK = 1024
SECONDS = 5
OUTFILE = "output.wav"

print('Start recording')


#now initializing looping_stream (the only audio stream)
stream = pa.open(
    format = FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    output = True,
    input_device_index = INDEVICE,
	output_device_index = OUTDEVICE,
    frames_per_buffer = CHUNK,
    start = True
)

frames = []  # Initialize array to store frames


# Store data in chunks for duration
for i in range(0, int(RATE / CHUNK * SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

# Stop and close the stream 
stream.stop_stream()
stream.close()
# Terminate the PortAudio interface
pa.terminate()

print('Finished recording')

# Save the recorded data as a WAV file
wf = wave.open(OUTFILE, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(pa.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()


spf = wave.open(OUTFILE, "r")

# Extract Raw Audio from Wav File
sample_freq = spf.getframerate()
n_samples = spf.getnframes()
signal = spf.readframes(-1)

spf.close()
t_audio = n_samples/sample_freq
sig_array = np.frombuffer(signal, dtype=np.int16)

times = np.linspace(0, t_audio, num=n_samples)


# If Stereo
if spf.getnchannels() == 2:
    print("Just mono files")
    sys.exit(0)

plt.figure(1)
plt.title("Signal Wave...")
plt.plot(times, sig_array)
plt.ylabel("Signal Wave")
plt.xlabel("Time (s)")
plt.xlim(0, t_audio)
plt.show()

