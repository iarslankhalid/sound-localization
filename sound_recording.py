import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

# Set up parameters
duration = 10  # Duration to record in seconds
fs = 44100  # Sample rate (try lowering to 16000 if needed)

# List all available audio devices
devices = sd.query_devices()
print("Available audio devices:")
for i, device in enumerate(devices):
    print(f"{i}: {device['name']} ({device['hostapi']})")

# Function to find USB microphones and ensure they're not the built-in mic
def find_usb_mics():
    usb_mics = []
    for i, device in enumerate(devices):
        if "usb" in device['name'].lower() and device['max_input_channels'] > 0:
            usb_mics.append((i, device['name']))
    return usb_mics

# Get USB microphones
usb_mics = find_usb_mics()

if len(usb_mics) < 2:
    raise RuntimeError("Less than 2 USB microphones detected. Ensure they are connected and not muted.")

# Assign mics to left and right based on order
mic_left_index = usb_mics[0][0]  # Index of the left mic
mic_right_index = usb_mics[1][0]  # Index of the right mic

# Print the selected devices for recording
print(f"Recording from: {usb_mics[0][1]} (Left mic)")
print(f"Recording from: {usb_mics[1][1]} (Right mic)")

# Buffers to store audio data
buffer_left = np.empty((0, 1), dtype=np.float32)
buffer_right = np.empty((0, 1), dtype=np.float32)

# Callback function to record audio from the left and right microphones
def audio_callback(indata, frames, time, status, mic_buffer):
    mic_buffer.append(indata.copy())

buffer_left_data = []
buffer_right_data = []

# Use InputStream to open both microphones simultaneously
with sd.InputStream(samplerate=fs, device=mic_left_index, channels=1, callback=lambda indata, frames, time, status: audio_callback(indata, frames, time, status, buffer_left_data)), \
     sd.InputStream(samplerate=fs, device=mic_right_index, channels=1, callback=lambda indata, frames, time, status: audio_callback(indata, frames, time, status, buffer_right_data)):

    print(f"Recording for {duration} seconds...")
    sd.sleep(duration * 1000)  # Wait for the duration

# Convert buffer data to numpy arrays for saving
buffer_left = np.concatenate(buffer_left_data)
buffer_right = np.concatenate(buffer_right_data)

# Check if audio was recorded
print("Left mic buffer size:", buffer_left.shape)
print("Right mic buffer size:", buffer_right.shape)

# Save the audio files as separate WAV files
wav.write("left_mic_clap.wav", fs, buffer_left)
wav.write("right_mic_clap.wav", fs, buffer_right)

print("Recording complete. Saved as 'left_mic.wav' and 'right_mic.wav'")
