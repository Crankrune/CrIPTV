import httpx

from m3u_utils import generate_playlist, parse_playlist

drewlive_url: str = "http://drewlive2423.duckdns.org:8081/DrewLive/MergedPlaylist.m3u8"


def generate_drewlive_playlist():
    playlist: str = httpx.get(drewlive_url).text
    playlist_data: list[dict] = parse_playlist(playlist)

    desired_grous: list[str] = [
        "A1xmedia Live Event | PPV",
        "A1xmedia UHD | 4K",
        "A1xmedia US Channels",
        "A1xmedia US Sports",
        "PlexTV - United States",
        "PlutoTV - United States",
        "RokuTV",
        "Roxiestream - WWE",
        "SamsungTVPlus - USA",
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

    with open("output/playlists/playlist_drewlive.m3u", "w", encoding="utf-8") as f:
        f.write(generate_playlist(desired_channels))
