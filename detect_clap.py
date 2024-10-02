import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time

# Parameters for detecting the clap
CLAP_THRESHOLD = 4000  # Adjust this value based on your needs
CHUNK = 1024  # Number of audio frames per buffer
RATE = 44100  # Sampling rate in Hz

def list_microphones(p):
    """Lists available audio input devices."""
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    
    print("Available Microphones:")
    
    for i in range(0, numdevices):
        device_info = p.get_device_info_by_index(i)
        if device_info.get('maxInputChannels') > 0:
            print(f"ID {i}: {device_info.get('name')}")

def detect_clap(data, threshold):
    """Detects a clap based on peak audio volume."""
    # Convert the byte data to numpy array
    audio_data = np.frombuffer(data, dtype=np.int16)

    # Get the peak value from the audio data
    peak = np.max(np.abs(audio_data))

    # Check if the peak exceeds the threshold (indicating a clap or loud sound)
    if peak > threshold:
        print(f"Clap detected! Peak value: {peak}")
        return True
    return False

def plot_audio_data(audio_data):
    """Plots the audio data."""
    plt.cla()  # Clear the previous plot
    plt.plot(audio_data)
    plt.ylim([-32768, 32767])  # Set the y-axis limits to the 16-bit PCM range
    plt.title("Real-Time Audio Data")
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.pause(0.01)  # Pause for a short time to allow the plot to update

def main():
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    # List available microphones
    list_microphones(p)
    
    # Ask user to select the microphone device
    device_id = int(input("Enter the microphone device ID you want to use: "))

    # Open the audio stream using the selected microphone
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=RATE,
                    input=True,
                    input_device_index=device_id,
                    frames_per_buffer=CHUNK)

    # Prepare the plot
    plt.ion()  # Interactive mode on, so plots update dynamically
    fig, ax = plt.subplots()

    print(f"Listening for claps using microphone ID {device_id}...")
    
    try:
        while True:
            # Read audio data from the stream
            data = stream.read(CHUNK, exception_on_overflow=False)
            
            # Convert data to numpy array for plotting
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Plot the audio data
            plot_audio_data(audio_data)

            # Detect clap
            detect_clap(data, CLAP_THRESHOLD)
            
            # Sleep for a bit to avoid CPU overuse
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("Stopped listening.")
    
    finally:
        # Close the stream and PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
