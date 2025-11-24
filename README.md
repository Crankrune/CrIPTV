# CrIPTV

This project provides a set of Python scripts and configuration files for generating and managing IPTV playlists and Electronic Program Guides (EPG) for various sources, including YouTube streams. The primary goal is to curate and update personalized IPTV channel lists and their corresponding EPG data.

## Project Structure

The project is organized into the following directories and files to ensure clarity and maintainability:

```
.
├── data/                 # Contains source data files used by the scripts.
│   ├── epg_links.txt     # (Placeholder for EPG source URLs, if any)
│   ├── iptv_database.json # Main database for IPTV channels.
│   └── youtube_channels.json # Configuration for YouTube channels to include.
├── output/               # Contains all generated output files.
│   ├── playlists/        # Generated M3U playlist files.
│   │   ├── playlist_broadcast.m3u
│   │   ├── playlist_essentials.m3u
│   │   ├── playlist_iptv.m3u
│   │   ├── playlist_news.m3u
│   │   └── playlist_sports.m3u
│   └── youtube_epg.xml   # Generated EPG for YouTube channels.
├── .git/                 # Git version control directory.
├── .gitignore            # Specifies files/directories to ignore in Git.
├── epg_generator.py      # Script to generate EPG XML files.
├── main.py               # Main entry point script to orchestrate updates.
├── m3u_utils.py          # Utility functions for M3U playlist parsing and generation.
├── playlists.yaml        # Configuration for custom playlist groupings.
├── update_and_commit.bat # Batch script to run updates and commit changes.
└── youtube_utils.py      # Utility functions for managing YouTube streams.
```

## How to Use

### Prerequisites

Before running the scripts, ensure you have the following installed:

*   **Python 3**: The scripts are written in Python 3.
*   **`yt-dlp`**: A command-line program to download videos from YouTube and other sites. Ensure it's in your system's PATH or accessible to the scripts.
*   **Python Libraries**: Install the required Python libraries using pip:
    ```bash
    pip install natsort ruamel.yaml
    ```

### Configuration

*   **`data/iptv_database.json`**: Edit this file to manage your main IPTV channel list.
*   **`data/youtube_channels.json`**: Configure the YouTube channels you want to include in your playlist.
*   **`playlists.yaml`**: Define custom playlist groupings based on `tvg-id` from your `iptv_database.json`.

### Running the Update Process

To update all playlists and EPG files, and then commit the changes to your Git repository, simply run the batch script:

```bash
.\update_and_commit.bat
```

This script will:
1.  Execute `main.py` which orchestrates:
    *   Reading data from `data/` files.
    *   Generating and saving M3U playlists to `output/playlists/`.
    *   Generating and saving the YouTube EPG to `output/youtube_epg.xml`.
2.  Stage all changes in Git.
3.  Commit the changes with a default message. (You may want to edit `update_and_commit.bat` to prompt for a custom commit message or review changes before committing.)
4.  Push the committed changes to your remote Git repository.

## Python Scripts Overview

*   **`main.py`**: The central script that calls functions from other modules to perform the entire update process.
*   **`m3u_utils.py`**: Contains generic utility functions for parsing and generating M3U playlist content.
*   **`epg_generator.py`**: Handles the creation of EPG XML data based on M3U playlist content.
*   **`youtube_utils.py`**: Manages fetching YouTube stream URLs and generating YouTube-specific playlist entries.

## Using the Generated Playlists and EPG

Once you have run the `update_and_commit.bat` script, your generated IPTV playlists (`.m3u` files) and the YouTube EPG (`youtube_epg.xml`) will be located in the `output/` directory.

To use these in an IPTV player (e.g., VLC, Kodi, IPTV Smarters Pro, Perfect Player):

1.  **Load the M3U Playlist**: Most IPTV players will have an option to "Add Playlist," "Load M3U File," or similar. Navigate to the `output/playlists/` directory and select the desired `.m3u` file (e.g., `playlist_iptv.m3u`).
2.  **Load the EPG (if applicable)**: For players that support external EPG sources (like Kodi or Perfect Player), look for an option to "Add EPG Source" or "Load XMLTV." Point it to `output/youtube_epg.xml`.

    *Note: The exact steps may vary depending on your specific IPTV player. Refer to your player's documentation for detailed instructions.*