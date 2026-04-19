# Smart Crochet Hook

**A wearable that tracks crochet movements using IMU data and provides real-time stitch analysis.**

The Smart Crochet Hook is a hardware-software integration project designed to capture the unique motion signatures of crochet stitches. Using an ESP32-C3 and an MPU6500 (accelerometer/gyroscope), the device streams 6-axis motion data to a Python backend for recording, live visualization, and frequency-domain analysis.

## Features

- High-Precision Sampling: Hardware-timed 50Hz data acquisition using FreeRTOS semaphores.
- Binary Protocol: Custom-packed binary data format for efficient serial communication with zero padding.
- Live Visualization: Integration with Teleplot (VS Code) for real-time motion graphing.
- Stitch Analysis: Python-based spectrogram generation (STFT) and magnitude analysis to identify stitch "signatures".
- Data Logging: Automated session recording saved to CSV for algorithm validation and signal analysis.

## System Components

- Hardware: ESP32-C3 Super Mini, MPU6500 IMU.
- Firmware: C++, Arduino Framework, FreeRTOS.
- Software: Python 3.11, Pandas, SciPy, Matplotlib.
- Tools: PlatformIO, VS Code, Teleplot.
- spectrogram.ipynb: Interactive workbench for parameter tuning.

## Repository Map

src/: Firmware source including register-level IMU configuration and timer-driven sampling.
receiver.py: Core driver for handling the serial handshake and packet unpacking.
data_stream.py: Utility for logging labeled motion sessions to CSV.
plot_stitch.py: Signal processing script for frequency-domain analysis.
live_plot.py: Real-time Teleplot streamer.

## Installation
1. Firmware Setup
- Install the PlatformIO extension in VS Code.
- Open the project in PlatformIO.
- Connect your ESP32-C3 Super Mini.
- Upload the firmware. The device waits for a handshake signal (s) before streaming.streaming.

2. Software Setup
Install the required dependencies:
```Bash
pip install pyserial pandas matplotlib scipy ipywidgets
```

## Usage

- Record Data: Run python data_stream.py to label and save sessions (e.g., "sc" for single crochet).
- Live View: Open Teleplot in VS Code and run python live_plot.py.
- Analyze: Run python plot_stitch.py to generate magnitude and spectrogram plots.
- Fine-tune: Launch spectrogram.ipynb to use the Filter Workbench and Magnitude Workbench for interactive parameter refining.

## Data Analysis

By applying a Butterworth band-pass filter, we isolate crochet-relevant frequencies from gravity and high-frequency noise. The resulting spectrograms provide a visual "fingerprint" for different types of stitches.


