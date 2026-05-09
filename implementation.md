# Local MP3 Downloader - Deployment Guide

This guide explains how to set up and run the MP3 Downloader on another Windows machine or access it from other devices on your local network.

## Prerequisites

1.  **Python 3.8+**: Ensure Python is installed and added to your system's PATH.
2.  **Internet Connectivity**: Required for the initial setup of `yt-dlp` and `ffmpeg` (via `static-ffmpeg`), and for downloading videos.

## Initial Setup on a New Device

1.  **Copy the Project Folder**: Copy the entire `mp3 download` folder to the target machine.
2.  **Open terminal/PowerShell**: Navigate to the project directory.
3.  **Install Dependencies**:
    ```powershell
    pip install -r requirements.txt
    ```

## Running the Server

1.  **Start the app**:
    ```powershell
    python app.py
    ```
2.  The server is configured to run on `0.0.0.0`, which means it is **publicly accessible** on your local network on port `5000`.

## Accessing from Other Devices (Phones, Tablets, Laptops)

To use the downloader from another device on the same Wi-Fi:

1.  **Find your host IP address**:
    - On the host Windows machine, run `ipconfig`.
    - Look for "IPv4 Address" (e.g., `192.168.1.10`).
2.  **Open a browser on your other device**:
    - Navigate to `http://<YOUR_IP>:5000` (e.g., `http://192.168.1.10:5000`).

## Important Configuration Notes

- **Browsers Cookies**: For age-restricted videos, the downloader is configured to try and fetch cookies from local browsers (`chrome`, `edge`, `firefox`, etc.). This only works if the host machine has those browsers installed and the user is logged into YouTube.
- **FFmpeg**: The script uses `static-ffmpeg`, which automatically downloads a portable version of FFmpeg the first time you run it. You do NOT need to install FFmpeg manually.
- **Downloads Folder**: All MP3 files are stored in the `downloads/` folder on the host machine.

## Troubleshooting

- **"Requested format is not available"**: Ensure `yt-dlp` is updated (`pip install -U yt-dlp`).
- **Firewall Issues**: If you can't access the site from another device, ensure your Windows Firewall allows incoming connections on port `5000`.
