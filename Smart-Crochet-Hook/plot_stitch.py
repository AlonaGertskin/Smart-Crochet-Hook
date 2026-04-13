import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import numpy as np
from scipy import signal

FOLDER = "stitch_tests"
SAMPLE_RATE = 50 

def list_files():
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
    fig.suptitle(f"Full 6-Axis Analysis: {os.path.basename(selected_file)}", fontsize=16)

    # Raw Data Rows
    ax_raw_acc = fig.add_subplot(gs[0, :])
    ax_raw_acc.plot(df['sec'], df['ax'], label='X', color='red', alpha=0.7)
    ax_raw_acc.plot(df['sec'], df['ay'], label='Y', color='green', alpha=0.7)
    ax_raw_acc.plot(df['sec'], df['az'], label='Z', color='blue', alpha=0.7)
    ax_raw_acc.set_ylabel("Accel (Raw)")
    ax_raw_acc.legend(loc='upper right'); ax_raw_acc.grid(True, alpha=0.3)

    ax_raw_gyr = fig.add_subplot(gs[1, :])
    ax_raw_gyr.plot(df['sec'], df['gx'], label='Roll', color='orange', alpha=0.7)
    ax_raw_gyr.plot(df['sec'], df['gy'], label='Pitch', color='purple', alpha=0.7)
    ax_raw_gyr.plot(df['sec'], df['gz'], label='Yaw', color='brown', alpha=0.7)
    ax_raw_gyr.set_ylabel("Gyro (Raw)")
    ax_raw_gyr.legend(loc='upper right'); ax_raw_gyr.grid(True, alpha=0.3)

    # 6 Spectrograms
    axes_labels = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']
    titles = ['Accel X', 'Accel Y', 'Accel Z', 'Gyro X', 'Gyro Y', 'Gyro Z']
    colors = ['magma', 'magma', 'magma', 'viridis', 'viridis', 'viridis']

    for i, col_name in enumerate(axes_labels):
        row, col = 2 + (i // 3), i % 3
        ax_spec = fig.add_subplot(gs[row, col])
        f, t, Sxx = signal.spectrogram(df[col_name].values, fs=SAMPLE_RATE, nperseg=64, noverlap=32)
        ax_spec.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10), shading='gouraud', cmap=colors[i])
        ax_spec.set_title(titles[i])
        if col == 0: ax_spec.set_ylabel('Freq (Hz)')
        if row == 3: ax_spec.set_xlabel('Time (s)')

    save_path = selected_file.replace(".csv", "_6axis_spectro.png")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(save_path)
    plt.close(fig)
    print(f"✅ Saved: {save_path}")

def generate_magnitude_analysis(df, selected_file):
    """Generates the simplified magnitude/orientation-independent analysis."""
    print(f"🖼️  Generating Magnitude analysis for: {selected_file}...")
    df['acc_mag'] = np.sqrt(df['ax']**2 + df['ay']**2 + df['az']**2)
    df['gyr_mag'] = np.sqrt(df['gx']**2 + df['gy']**2 + df['gz']**2)

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(12, 16))
    fig.suptitle(f"Magnitude Analysis: {os.path.basename(selected_file)}", fontsize=16)

    ax1.plot(df['sec'], df['acc_mag'], color='black')
    ax1.set_title("Accel Magnitude"); ax1.grid(True, alpha=0.3)

    f_a, t_a, Sxx_a = signal.spectrogram(df['acc_mag'].values, fs=SAMPLE_RATE, nperseg=64, noverlap=32)
    ax2.pcolormesh(t_a, f_a, 10 * np.log10(Sxx_a + 1e-10), shading='gouraud', cmap='magma')
    ax2.set_ylabel('Freq (Hz)')

    ax3.plot(df['sec'], df['gyr_mag'], color='darkblue')
    ax3.set_title("Gyro Magnitude"); ax3.grid(True, alpha=0.3)

    f_g, t_g, Sxx_g = signal.spectrogram(df['gyr_mag'].values, fs=SAMPLE_RATE, nperseg=64, noverlap=32)
    ax4.pcolormesh(t_g, f_g, 10 * np.log10(Sxx_g + 1e-10), shading='gouraud', cmap='viridis')
    ax4.set_ylabel('Freq (Hz)'); ax4.set_xlabel('Time (s)')

    save_path = selected_file.replace(".csv", "_magnitude_spectro.png")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(save_path)
    plt.close(fig)
    print(f"✅ Saved: {save_path}")

def main():
    files = list_files()
    if not files: return
    choice = input("\n🔢 Number to plot (or 'all' / Enter for latest): ").strip().lower()
    
    to_process = files if choice == "all" else [files[-1]] if choice == "" else [files[int(choice)]]

    for f in to_process:
        df = pd.read_csv(f)
        df['sec'] = (df['ms'] - df['ms'].iloc[0]) / 1000.0
        generate_full_analysis(df, f)
        generate_magnitude_analysis(df, f)

if __name__ == "__main__":
    main()