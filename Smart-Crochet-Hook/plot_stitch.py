import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

FOLDER = "stitch_tests"

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

def plot_and_save():
    files = list_files()
    if not files: return

    choice = input("\n🔢 Number to plot (or 'all' / Enter for latest): ").strip().lower()
    
    # Decide which files to process
    to_process = []
    if choice == "all":
        to_process = files
    elif choice == "":
        to_process = [files[-1]]
    else:
        try:
            to_process = [files[int(choice)]]
        except:
            print("❌ Invalid selection."); return

    for selected_file in to_process:
        print(f"🖼️  Generating plot for: {selected_file}...")
        df = pd.read_csv(selected_file)
        df['sec'] = (df['ms'] - df['ms'].iloc[0]) / 1000.0

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        fig.suptitle(f"Stitch Analysis: {os.path.basename(selected_file)}", fontsize=14)

        # Accelerometer
        ax1.plot(df['sec'], df['ax'], label='X', color='red', alpha=0.7)
        ax1.plot(df['sec'], df['ay'], label='Y', color='green', alpha=0.7)
        ax1.plot(df['sec'], df['az'], label='Z', color='blue', alpha=0.7)
        ax1.set_ylabel("Accel (Raw)")
        ax1.legend(loc='upper right'); ax1.grid(True, alpha=0.3)

        # Gyroscope
        ax2.plot(df['sec'], df['gx'], label='Roll', color='orange', alpha=0.7)
        ax2.plot(df['sec'], df['gy'], label='Pitch', color='purple', alpha=0.7)
        ax2.plot(df['sec'], df['gz'], label='Yaw', color='brown', alpha=0.7)
        ax2.set_ylabel("Gyro (Raw)"); ax2.set_xlabel("Time (seconds)")
        ax2.legend(loc='upper right'); ax2.grid(True, alpha=0.3)

        # Save the file with the same name but .png extension
        save_path = selected_file.replace(".csv", ".png")
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close(fig) # Closes the plot so it doesn't pop up
        print(f"✅ Saved to: {save_path}")

if __name__ == "__main__":
    plot_and_save()