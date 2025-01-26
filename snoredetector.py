import sounddevice as sd
import numpy as np
import time
from scipy.fft import fft
import os  # Import the 'os' module for running external programs

# --- Configuration ---
DURATION = 0.2
SAMPLING_RATE = 44100
CHUNK_SIZE = 1024
THRESHOLD_SNORE_AMPLITUDE = 0.1
FREQUENCY_RANGE_SNORE = (100, 1000)
THRESHOLD_SNORE_FREQUENCY_ENERGY = 10.0
SNORE_COUNT_THRESHOLD = 3  # Number of snores within the time window to trigger action
TIME_WINDOW_SECONDS = 60  # Time window in seconds
PROGRAM_TO_RUN = "echo 'Snore Action Triggered!'"  # Replace with your program/command

# --- Global variable to keep track of snore times ---
snore_timestamps = []

# --- Functions ---


def record_audio(duration=DURATION, fs=SAMPLING_RATE):
    """Records audio for a short duration."""
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, blocking=True)
    return recording.flatten()


def calculate_amplitude(audio_chunk):
    """Calculates the amplitude (RMS) of an audio chunk."""
    amplitude = np.sqrt(np.mean(audio_chunk**2))
    return amplitude


def analyze_frequency(audio_chunk, fs=SAMPLING_RATE, freq_range=FREQUENCY_RANGE_SNORE):
    """Performs frequency analysis using FFT and calculates energy in a frequency range."""
    N = len(audio_chunk)
    yf = fft(audio_chunk)
    yf_abs = np.abs(yf[: N // 2])
    xf = np.fft.fftfreq(N, 1 / fs)[: N // 2]

    start_freq_index = np.argmin(np.abs(xf - freq_range[0]))
    end_freq_index = np.argmin(np.abs(xf - freq_range[1]))
    frequency_energy = np.sum(yf_abs[start_freq_index : end_freq_index + 1]) / N

    return frequency_energy, xf, yf_abs


def is_snore(audio_chunk):
    """Detects if a snore is present based on amplitude AND frequency content."""
    amplitude = calculate_amplitude(audio_chunk)
    frequency_energy, xf, yf_abs = analyze_frequency(audio_chunk)

    is_possible_snore = False

    if amplitude > THRESHOLD_SNORE_AMPLITUDE:
        print("High Amplitude Detected")
        is_possible_snore = True

    if frequency_energy > THRESHOLD_SNORE_FREQUENCY_ENERGY:
        print(
            f"High Frequency Energy ({FREQUENCY_RANGE_SNORE} Hz): {frequency_energy:.2f}"
        )
        print("Frequency Range Snore Detected")
        is_possible_snore = True

    return is_possible_snore  # Return True/False if it's a potential snore, action is handled in main_loop


def trigger_program():
    """Executes the external program using os.system."""
    print(f"Triggering program: {PROGRAM_TO_RUN}")
    os.system(
        PROGRAM_TO_RUN
    )  # Be cautious with os.system, consider subprocess.run for more control


def main_loop():
    """The main loop that continuously monitors audio, detects snores, and triggers program."""
    global snore_timestamps  # Use the global snore_timestamps list
    print("Snore Detection Started (with Program Trigger)...")
    while True:
        audio_data = record_audio()
        if is_snore(audio_data):
            current_time = time.time()
            snore_timestamps.append(current_time)  # Add timestamp of detection

            # --- Clean up old timestamps ---
            snore_timestamps[:] = [
                ts
                for ts in snore_timestamps
                if current_time - ts <= TIME_WINDOW_SECONDS
            ]

            snore_count = len(snore_timestamps)
            print(
                f"Snore Detected! Snore count in last {TIME_WINDOW_SECONDS} seconds: {snore_count}"
            )

            if snore_count >= SNORE_COUNT_THRESHOLD:
                trigger_program()
                snore_timestamps = (
                    []
                )  # Reset the count after triggering (optional - depends on desired behavior)
                print("Snore count reset.")  # Feedback that count was reset
        time.sleep(0.1)


if __name__ == "__main__":
    main_loop()
