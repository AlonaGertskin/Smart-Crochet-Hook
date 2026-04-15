import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import numpy as np
from scipy import signal
import matplotlib.colors as colors

# --- CONFIGURATION ---
FOLDER = "stitch_tests"
SAMPLE_RATE = 50  # From config.h

# --- EXPERIMENT PARAMETERS ---
# Adjust these to change the look of your "blocks"
N_PER_SEG = 256   # Length of each segment (~1.28s)
N_OVERLAP = 230   # Higher overlap (56/64 = 87%) for smoother transitions
N_FFT = 300      # Pads with zeros for sharper frequency resolution

# --- DISPLAY PARAMETERS ---
# V_MIN: Increase this (e.g., -20 or -10) to black out background noise
V_MIN = -20
COLOR_MAP_ACCEL = 'inferno' 
COLOR_MAP_GYRO = 'hot'

# --- FILTER PARAMETERS ---
LOW_CUT = 0.5    # Removes gravity/slow drift
HIGH_CUT = 10  # Removes high-frequency jitter
FILTER_ORDER = 4

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    """Applies a band-pass filter to keep only crochet-relevant frequencies."""
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    y = signal.filtfilt(b, a, data)
    return y

def list_files():
    """Lists all CSV files in the stitch_tests folder."""
    files = glob.glob(f'{FOLDER}/*.csv')
    files.sort(key=os.path.getctime)
    if not files:
        print(f"❌ No files found in '{FOLDER}'")
        return None
    
    print("\n📚 Available Stitch Recordings:")
    for i, file in enumerate(files):
        print(f"[{i}] {os.path.basename(file)}")
    return files

def generate_full_analysis(df, selected_file):
    """Generates the 6-axis detailed spectrogram grid."""
    print(f"🖼️  Generating 6-axis analysis for: {selected_file}...")
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(4, 3)
    
    title_str = (f"6-Axis Analysis | p={N_PER_SEG}, o={N_OVERLAP}, fft={N_FFT}\n"
                 f"File: {os.path.basename(selected_file)}")
    fig.suptitle(title_str, fontsize=16)

    # 1. Raw Accelerometer
    ax_raw_acc = fig.add_subplot(gs[0, :])
    ax_raw_acc.plot(df['sec'], df['ax'], label='X', color='red', alpha=0.7)
    ax_raw_acc.plot(df['sec'], df['ay'], label='Y', color='green', alpha=0.7)
    ax_raw_acc.plot(df['sec'], df['az'], label='Z', color='blue', alpha=0.7)
    ax_raw_acc.set_ylabel("Accel (Raw)")
    ax_raw_acc.legend(loc='upper right'); ax_raw_acc.grid(True, alpha=0.3)

    # 2. Raw Gyroscope
    ax_raw_gyr = fig.add_subplot(gs[1, :])
    ax_raw_gyr.plot(df['sec'], df['gx'], label='Roll', color='orange', alpha=0.7)
    ax_raw_gyr.plot(df['sec'], df['gy'], label='Pitch', color='purple', alpha=0.7)
    ax_raw_gyr.plot(df['sec'], df['gz'], label='Yaw', color='brown', alpha=0.7)
    ax_raw_gyr.set_ylabel("Gyro (Raw)")
    ax_raw_gyr.legend(loc='upper right'); ax_raw_gyr.grid(True, alpha=0.3)

    # 3. 6 Spectrograms
    axes_labels = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']
    titles = ['Accel X', 'Accel Y', 'Accel Z', 'Gyro X', 'Gyro Y', 'Gyro Z']
    
    for i, col_name in enumerate(axes_labels):
        row, col = 2 + (i // 3), i % 3
        ax_spec = fig.add_subplot(gs[row, col])
        
        # Spectrogram Math
        f, t, Sxx = signal.spectrogram(
            df[col_name].values, 
            fs=SAMPLE_RATE, 
            nperseg=N_PER_SEG, 
            noverlap=N_OVERLAP, 
            nfft=N_FFT
        )
        
        cmap = 'magma' if i < 3 else 'viridis'
        ax_spec.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud', cmap=cmap)
        ax_spec.set_title(titles[i])
        if col == 0: ax_spec.set_ylabel('Freq (Hz)')
        if row == 3: ax_spec.set_xlabel('Time (s)')

    # Parameter-based filename
    suffix = f"_6axis_n{N_FFT}_p{N_PER_SEG}_o{N_OVERLAP}.png"
    save_path = selected_file.replace(".csv", suffix)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(save_path)
    plt.close(fig)
    print(f"✅ Saved: {save_path}")

def generate_magnitude_analysis(df, selected_file):
    print(f"🖼️  Generating Enhanced Display Analysis for: {selected_file}...")
    
    raw_acc_mag = np.sqrt(df['ax']**2 + df['ay']**2 + df['az']**2)
    raw_gyr_mag = np.sqrt(df['gx']**2 + df['gy']**2 + df['gz']**2)

    # Apply High-Pass to center at zero
    df['acc_mag'] = butter_bandpass_filter(raw_acc_mag, LOW_CUT, HIGH_CUT, SAMPLE_RATE, FILTER_ORDER)
    df['gyr_mag'] = butter_bandpass_filter(raw_gyr_mag, LOW_CUT, HIGH_CUT, SAMPLE_RATE, FILTER_ORDER)
    # --- NORMALIZATION: Divide by the Max ---
    # We use np.abs() just in case there are negative swings from the high-pass filter
    if raw_acc_mag.max() != 0:
        df['acc_mag'] = df['acc_mag'] / np.abs(df['acc_mag']).max()

    if raw_gyr_mag.max() != 0:
        df['gyr_mag'] = df['gyr_mag'] / np.abs(df['gyr_mag']).max()
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 16))
    fig.suptitle(f"Enhanced Display Analysis | vmin={V_MIN}, p={N_PER_SEG}\n{os.path.basename(selected_file)}", fontsize=16)

    # 1. Accel Time Graph
    ax1.plot(df['sec'], df['acc_mag'], color='black', linewidth=0.8)
    ax1.set_title("High-Pass Accel Magnitude"); ax1.grid(True, alpha=0.3)

    # 3. Gyro Time Graph
    ax3.plot(df['sec'], df['gyr_mag'], color='darkblue', linewidth=0.8)
    ax3.set_title("High-Pass Gyro Magnitude"); ax3.grid(True, alpha=0.3)

    # --- The Display Trick ---
    # We use LogNorm to define a 'floor'. 
    # Anything below the floor becomes the darkest color.
    # This makes the 'blocks' of the stitches stand out.
    
    for target_ax, data, title, cmap in [(ax2, df['acc_mag'], "Accel", 'magma'), 
                                         (ax4, df['gyr_mag'], "Gyro", 'hot')]:
        
        f, t, Sxx = signal.spectrogram(data.values, fs=SAMPLE_RATE, nperseg=32, noverlap=30, nfft=64)
        
        # We use LogNorm to set a dynamic range. 
        # Adjust 'vmin' to make the background darker or lighter.
        pcm = target_ax.pcolormesh(t, f, Sxx, 
                                   norm=colors.LogNorm(vmin=Sxx.max()/1000, vmax=Sxx.max()), 
                                   shading='gouraud', 
                                   cmap=cmap)
        target_ax.set_ylim(0, 12)
        target_ax.set_title(f"Logarithmic {title} Spectrogram")
        fig.colorbar(pcm, ax=target_ax, label='Power')

    # Parameter-based filename
    suffix = f"_mag_l{LOW_CUT}_h{HIGH_CUT}_p{N_PER_SEG}_o{N_OVERLAP}.png" 
    save_path = selected_file.replace(".csv", suffix)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(save_path)
    plt.close(fig)
    print(f"✅ Saved: {save_path}")

def main():
    files = list_files()
    if not files: return
    
    choice = input("\n🔢 Number to plot (or 'all' / Enter for latest): ").strip().lower()
    
    if choice == "all":
        to_process = files
    elif choice == "":
        to_process = [files[-1]]
    else:
        try:
            to_process = [files[int(choice)]]
        except:
            print("❌ Invalid selection."); return

    for f in to_process:
        df = pd.read_csv(f)
        # Normalize time to start at 0
        df['sec'] = (df['ms'] - df['ms'].iloc[0]) / 1000.0
        
        generate_full_analysis(df, f)
        generate_magnitude_analysis(df, f)

if __name__ == "__main__":
    main()