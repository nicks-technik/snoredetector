import sounddevice as sd
import numpy as np
import time
from scipy.fft import fft  # For Fast Fourier Transform (FFT)

# --- Configuration ---
SAMPLING_RATE = 44100
CHUNK_SIZE = 1024
# Amplitude threshold (you might still want a basic amplitude check)
THRESHOLD_SNORE_AMPLITUDE = 0.08  # Adjusted amplitude threshold, tune as needed
# Frequency range where snores are expected (Hz) - adjust these!
FREQUENCY_RANGE_SNORE = (100, 1000)  # Example range, needs experimentation
THRESHOLD_SNORE_FREQUENCY_ENERGY = (
    10.0  # Threshold for energy in snore frequency range - tune!
)

# --- Functions ---


def record_audio(duration=0.1, fs=SAMPLING_RATE):
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
    yf_abs = np.abs(
        yf[: N // 2]
    )  # Get magnitude spectrum, consider only positive frequencies
    xf = np.fft.fftfreq(N, 1 / fs)[: N // 2]  # Frequency axis

    # Calculate energy within the specified frequency range
    start_freq_index = np.argmin(
        np.abs(xf - freq_range[0])
    )  # Find index closest to start frequency
    end_freq_index = np.argmin(
        np.abs(xf - freq_range[1])
    )  # Find index closest to end frequency
    frequency_energy = (
        np.sum(yf_abs[start_freq_index : end_freq_index + 1]) / N
    )  # Average energy in the range

    return (
        frequency_energy,
        xf,
        yf_abs,
    )  # return frequency energy for detection, and frequency data for potential visualization/debugging


def is_snore(audio_chunk):
    """Detects if a snore is present based on amplitude AND frequency content."""
    amplitude = calculate_amplitude(audio_chunk)
    frequency_energy, xf, yf_abs = analyze_frequency(audio_chunk)

    is_possible_snore = False  # Flag to track if any snore criteria is met

    if (
        amplitude > THRESHOLD_SNORE_AMPLITUDE
    ):  # Basic amplitude check - can be adjusted or removed
        print("High Amplitude Detected")  # Debugging output
        is_possible_snore = True  # Consider it a possible snore if amplitude is high

    if frequency_energy > THRESHOLD_SNORE_FREQUENCY_ENERGY:
        print(
            f"High Frequency Energy ({FREQUENCY_RANGE_SNORE} Hz): {frequency_energy:.2f}"
        )  # Debugging output
        print("Frequency Range Snore Detected")
        is_possible_snore = (
            True  # Consider it a possible snore if frequency energy is high
        )

    if (
        is_possible_snore
    ):  # Only return True if *any* snore criteria was met (you can change to 'and' for stricter criteria)
        return True
    return False


def main_loop():
    """The main loop that continuously monitors audio and detects snores."""
    print("Snore Detection Started (Frequency Analysis)...")
    while True:
        audio_data = record_audio()
        if is_snore(audio_data):
            print("Snore Detected!")
        time.sleep(0.1)


if __name__ == "__main__":
    main_loop()
