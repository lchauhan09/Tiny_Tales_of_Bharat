# Tiny Tales of Bharat 🕉️

A semi-automated YouTube channel creating 6-minute, kid-friendly mythological videos.

## 🚀 Setup

1.  **Install FFmpeg**: Run the installation script to set up FFmpeg locally:
    ```powershell
    # Run in PowerShell
    ./automation/utils/install_ffmpeg.ps1
    ```
2.  **Add to Path**: Ensure the `tools/` directory is in your system's Environment Variables.

## 📁 Project Structure

- **`automation/`**:
  - `generate_script.py`: The "brain" that picks the next story.
  - `generate_prompts.py`: Extracts image prompts.
  - `assemble_video.py`: The master assembly script with logging, fallbacks, and progress tracking.
- **`tools/`**: Local FFmpeg binaries.
- **`videos/rough_cuts/`**: Output directory for generated drafts.

## ✨ Features

- **Dynamic Pacing**: Video durations automatically match the narrator's speed.
- **Robust Pipeline**: Automatic fallback images and placeholder intro/outro generation.
- **Progress Tracking**: Real-time progress bars during assembly.
- **Professional Logs**: Comprehensive logging in `automation/logs/assemble.log`.