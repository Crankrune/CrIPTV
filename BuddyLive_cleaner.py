import json
import urllib.request
from urllib.error import HTTPError, URLError

from m3uparse import Channel, Playlist

PLAYLIST_URL: str = (
    "https://raw.githubusercontent.com/BuddyChewChew/My-Streams/refs/heads/main/tv.m3u"
)


def get_clean_channels() -> list[Channel] | None:
    """Fetches the playlist, loads the JSON, and generates the base cleaned channels."""
    try:
        with urllib.request.urlopen(PLAYLIST_URL, timeout=10) as response:
            m3u_text = response.read().decode("utf-8")
    except (HTTPError, URLError):
        print(f"Unable to grab playlist from {PLAYLIST_URL!r}, no playlist generated.")
        return None

    playlist = Playlist.parse(m3u_text)

    clean_channels: list[Channel] = []
    for channel in playlist.channels:
        if len(channel.extra_lines) > 0:
            continue
        clean_channels.append(channel)

    return clean_channels


def make_clean_playlist(clean_channels: list[Channel]) -> None:
    """Creates and writes the clean playlist."""
    clean_playlist: Playlist = Playlist(
        channels=clean_channels,
        header_attrs={
            "x-tvg-url": "https://raw.githubusercontent.com/doms9/iptv/refs/heads/default/M3U8/TV.xml"
        },
    )

    with open(
        "output/playlists/playlist_BuddyLive_clean.m3u", mode="w", encoding="utf-8"
    ) as fl:
        fl.write(clean_playlist.to_m3u())


def main() -> None:
    """Main execution block to run the script steps."""
    clean_channels = get_clean_channels()

    # Exit if the playlist couldn't be fetched
    if clean_channels is None:
        return

    make_clean_playlist(clean_channels)


if __name__ == "__main__":
    main()
