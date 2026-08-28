import json
import urllib.request
from urllib.error import HTTPError, URLError

from m3uparse import Channel, Playlist

PLAYLIST_URL: str = "https://tv.crankrune.dedyn.io/playlist.m3u8"


def main() -> None:
    with open("data/clean_info.json", mode="r", encoding="utf-8") as f:
        clean_info = json.load(f)

    try:
        with urllib.request.urlopen(PLAYLIST_URL, timeout=10) as response:
            m3u_text = response.read().decode("utf-8")
    except (HTTPError, URLError):
        print(f"Unable to grab playlist from {PLAYLIST_URL!r}, no playlist generated.")
        return

    playlist = Playlist.parse(m3u_text)

    clean_channels: list[Channel] = []
    for channel in playlist.channels:
        if channel.title in clean_info:
            chan: Channel = Channel(
                title=clean_info[channel.title]["cleaned_name"],
                attrs={
                    "tvg-logo": clean_info[channel.title]["logo_url"],
                    "tvg-id": clean_info[channel.title]["epg_id"],
                },
                url=channel.url,
            )
            clean_channels.append(chan)

    clean_working_channels: list[Channel] = [
        channel for channel in clean_channels if channel.check_status()
    ]

    clean_playlist: Playlist = Playlist(
        channels=clean_channels,
        header_attrs={
            "x-tvg-url": "https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz"
        },
    )
    clean_working_playlist: Playlist = Playlist(
        channels=clean_working_channels,
        header_attrs={
            "x-tvg-url": "https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz"
        },
    )

    with open(
        "output/playlists/playlist_CrankTV_clean.m3u8", mode="w", encoding="utf-8"
    ) as fl:
        fl.write(clean_playlist.to_m3u())

    with open(
        "output/playlists/playlist_CrankTV_working.m3u8", mode="w", encoding="utf-8"
    ) as fl:
        fl.write(clean_working_playlist.to_m3u())
