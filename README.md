# CrIPTV

This project provides a set of Python scripts to generate and manage IPTV playlists (`.m3u`) and Electronic Program Guides (`.xml`). It's designed to be highly configurable and is fully automated using GitHub Actions to ensure your playlists and EPG data are always up-to-date.

## Project Structure

The project is organized into a clean and maintainable structure that separates data, source code, and generated output:

```
.
├── .github/
│   └── workflows/
│       └── main.yml        # GitHub Actions workflow for automated updates.
├── data/
│   ├── iptv_database.json  # Main database for IPTV channels.
│   ├── youtube_channels.json # Configuration for YouTube channels.
│   └── epg_links.txt       # (Placeholder for EPG source URLs).
├── output/
│   ├── playlists/
│   │   ├── playlist_iptv.m3u
│   │   ├── playlist_broadcast.m3u
│   │   └── ... (other generated playlists)
│   └── youtube_epg.xml     # Generated EPG for YouTube channels.
├── .gitignore
├── main.py                 # Main script to orchestrate all tasks.
├── m3u_utils.py            # Utilities for M3U playlist handling.
├── epg_generator.py        # Script to generate EPG XML files.
├── youtube_utils.py        # Utilities for handling YouTube streams.
├── playlists.yaml          # Configuration for custom playlist groupings.
└── update_and_commit.bat   # (Optional) Batch script for local manual updates.
```

## Automation with GitHub Actions

This repository is configured with a GitHub Actions workflow that automatically regenerates the playlists and EPG. The workflow runs on the following triggers:

1.  **On Push**: Every time a change is pushed to the `main` branch.
2.  **On a Schedule**: Runs daily at midnight UTC to keep stream links and data fresh.
3.  **Manually**: You can trigger it manually from the "Actions" tab in your GitHub repository.

The workflow automatically commits and pushes any changes to the `output/` directory back to the repository.

## How to Use

### Configuration

To customize your playlists, edit the files in the `data/` directory and the main `playlists.yaml` file:

*   **`data/iptv_database.json`**: Manage your primary list of IPTV channels here.
*   **`data/youtube_channels.json`**: Define which YouTube channels you want to include.
*   **`playlists.yaml`**: Create custom, filtered playlists by specifying which `tvg-id`s to include in each file.

### Using the Generated Playlists and EPG

The generated files are intended to be used with any IPTV player that supports `.m3u` playlists and `XMLTV` EPG formats (e.g., VLC, Kodi, IPTV Smarters, Perfect Player).

1.  **Find the File URL**: In your GitHub repository, navigate to the `output/` directory, select the desired file (e.g., `playlist_iptv.m3u`), and get its raw URL.
2.  **Load into Player**:
    *   **Playlist**: In your IPTV player, find the option to "Add Playlist from URL" (or similar) and paste the raw URL of your `.m3u` file.
    *   **EPG**: For players that support it, find the option to "Add EPG from URL" and paste the raw URL of the `youtube_epg.xml` file.

This allows your IPTV player to always pull the latest version of your files directly from your repository.
