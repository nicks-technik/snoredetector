# sudo apt-get install portaudio19-dev
# pip install --no-cache-dir --force-reinstall sounddevice numpy

# --- Import necessary libraries ---
import sounddevice as sd  # For recording audio
import numpy as np  # For numerical operations (audio data is numpy arrays)
import time  # For time-related functions (like pausing between checks)

# --- Configuration ---
SAMPLING_RATE = 44100  # Standard audio sampling rate (samples per second)
CHUNK_SIZE = 1024  # Number of samples to process at a time
THRESHOLD_SNORE_AMPLITUDE = 0.1  # Example threshold - you'll need to tune this
# FREQUENCY_RANGE_SNORE = ( ... ) # Optional: Define a frequency range for snores

# --- Functions ---


def record_audio(duration=0.1, fs=SAMPLING_RATE):
    """Records audio for a short duration."""
    recording = sd.rec(
        int(duration * fs), samplerate=fs, channels=1, blocking=True
    )  # Mono recording
    return recording.flatten()  # Flatten to 1D array if stereo


def calculate_amplitude(audio_chunk):
    """Calculates the amplitude (RMS) of an audio chunk."""
    amplitude = np.sqrt(np.mean(audio_chunk**2))  # Root Mean Square
    return amplitude


# def analyze_frequency(audio_chunk): # Optional: For frequency analysis
#     """Performs frequency analysis on an audio chunk (e.g., using FFT)."""
#     # ... (Implementation of frequency analysis - FFT, etc.) ...
#     pass # Placeholder for now


def is_snore(audio_chunk):
    """Detects if a snore is present in the audio chunk based on features."""
    amplitude = calculate_amplitude(audio_chunk)
    if amplitude > THRESHOLD_SNORE_AMPLITUDE:
        # You could add more sophisticated checks here, like frequency analysis
        print("Possible Snore (Amplitude Threshold)")  # Basic indication
        return True
    return False


def main_loop():
    """The main loop that continuously monitors audio and detects snores."""
    print("Snore Detection Started...")
    while True:
        audio_data = record_audio()
        if is_snore(audio_data):
            print("Snore Detected!")  # Or trigger another action here
        time.sleep(0.1)  # Short pause to avoid constant processing


if __name__ == "__main__":
    main_loop()
