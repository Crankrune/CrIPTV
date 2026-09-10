import re
from copy import deepcopy

import httpx

from m3u_utils import generate_playlist, parse_playlist

drewlive_url: str = "http://drewlive2423.duckdns.org:8081/DrewLive/MergedPlaylist.m3u8"


def generate_drewlive_playlist() -> None:
    try:
        playlist: str = httpx.get(drewlive_url).text
    except httpx.ConnectTimeout:
        print("DrewLive is currently unresponsive, no playlist generated.")
        return
    playlist_data: list[dict] = parse_playlist(playlist_content=playlist)

    desired_grous: list[str] = [
        "A1xmedia Live Event | PPV",
        "A1xmedia UHD | 4K",
        "A1xmedia US Channels",
        "A1xmedia US Sports",
        "LGTV - United States",
        "MoveOnJoy",
        "PlexTV - United States",
        "PlutoTV - United States",
        "PlutoTV",
        "RokuTV",
        "Roxiestream - WWE",
        "SamsungTVPlus - USA",
        "Sharkstreams - NBA",
        "Sharkstreams - UFC",
        "Sharkstreams - WWE",
        "TubiTV",
        "Xumo Streams",
    ]
    desired_channels: list[dict] = []

    groups: list[str] = []
    for channel in playlist_data:
        group_title: str = channel["group-title"]
        if group_title not in groups:
            groups.append(group_title)

        if group_title in desired_grous:
            desired_channels.append(channel)

    with open(
        file="output/playlists/playlist_drewlive.m3u",
        mode="w",
        encoding="utf-8",
    ) as f:
        f.write(generate_playlist(playlist_data=desired_channels))


def generate_ultratv_playlist() -> None:
    try:
        playlist: str = httpx.get(drewlive_url).text
    except httpx.ConnectTimeout:
        print("DrewLive is currently unresponsive, no playlist generated.")
        return
    playlist_data: list[dict] = parse_playlist(playlist_content=playlist)

    desired_channels: list[dict] = []

    for channel in playlist_data:
        channel_url: str = channel.get("url", "")
        if "ultratv.one" in channel_url.lower():
            new_channel: dict = deepcopy(channel)
            new_channel["group-title"] = "UltraTV One"
            desired_channels.append(new_channel)

    desired_channels.sort(key=lambda d: d.get("name", "").casefold())

    with open(
        file="output/playlists/playlist_ultratv.m3u",
        mode="w",
        encoding="utf-8",
    ) as f:
        f.write(generate_playlist(playlist_data=desired_channels))


def generate_ultratv_clean_playlist() -> None:
    try:
        playlist: str = httpx.get(drewlive_url).text
    except httpx.ConnectTimeout:
        print("DrewLive is currently unresponsive, no playlist generated.")
        return
    playlist_data: list[dict] = parse_playlist(playlist_content=playlist)

    desired_channels: list[dict] = []

    tvg_id_str: str = (
        r"(WRSP|WAND|WCIA|WICD|WICS|WISN|WMBD|WDKY)\.|PBS.WILL|Starz\.|Cinemax\.|Showtime\..*\.us|HBO\..*\.us|ESPN\..*\.us|Fox\.Sports\.[12]|Big\.Ten.*\.us|nbc\.news\.now\.us|nbc\.us|cbs\.us|abc\.us|fox\.us|smithsonian\.channel\.us|magnolia\.network\.us|hgtv\.(east|west)\.us|fx\.(east|west)\.us|fxx\.us|fxm\.us|game\.show\.gsn\.us|food\.network\.(east|west)\.us|newsnation\.us|fox\.news\.channel\.hd\.us|cnn\.us|msnbc\.us|sky.sports.nfl.fhd.uk|tnt\.us|tnt\.west\.us|tnt\.sports\.us|tbs\.(east|west)\.us|trutv\.east\.us|usa\.network\.us|vice\.us"
    )

    for channel in playlist_data:
        channel_url: str = channel.get("url", "")
        channel_id: str = channel.get("tvg-id", "")
        if not re.search(tvg_id_str, channel_id, flags=re.I):
            continue
        if "ultratv.one" in channel_url.lower():
            new_channel: dict = deepcopy(channel)
            new_channel["group-title"] = "UltraTV One"
            desired_channels.append(new_channel)

    desired_channels.sort(key=lambda d: d.get("name", "").casefold())

    with open(
        file="output/playlists/playlist_ultratv_clean.m3u",
        mode="w",
        encoding="utf-8",
    ) as f:
        f.write(generate_playlist(playlist_data=desired_channels))


if __name__ == "__main__":
    generate_ultratv_clean_playlist()
