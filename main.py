import json
import re
from pprint import pprint

from natsort import natsorted
from ruamel.yaml import YAML

from check_streams import main as check_streams
from epg_generator import write_youtube_epg_file
from m3u_utils import generate_playlist
from youtube_utils import update_stream_urls, write_playlist


def generate_iptv_playlists():
    """
    Updates the main playlist and specific playlists from the JSON data.
    """
    print("Starting IPTV playlist generation...")
    with open("data/iptv_database.json", "r", encoding="utf-8") as f:
        playlist_data = json.load(f)

    # Update the main M3U file
    playlist_content = generate_playlist(
        natsorted(playlist_data, key=lambda ch: ch["name"].casefold())
    )
    with open("output/playlists/playlist_iptv.m3u", "w", encoding="utf-8") as f:
        f.write(playlist_content)
    print("Generated output/playlists/playlist_iptv.m3u")

    # Update the working M3U file
    with open("data/iptv_database_info.json", "r", encoding="utf-8") as f:
        playlist_data = json.load(f)

    playlist_data = [channel for channel in playlist_data if channel["working"] is True]

    playlist_content = generate_playlist(
        natsorted(playlist_data, key=lambda ch: ch["name"].casefold())
    )
    with open("output/playlists/playlist_iptv_working.m3u", "w", encoding="utf-8") as f:
        f.write(playlist_content)
    print("Generated output/playlists/playlist_iptv_working.m3u")

    # Update specific playlists from YAML configuration
    yaml = YAML(typ="safe")
    with open("playlists.yaml", "r") as f:
        playlists = yaml.load(f)

    for playlist, data in playlists["playlists"].items():
        channel_ids = data["ids"]
        matching_channels = [
            channel for channel in playlist_data if channel["tvg-id"] in channel_ids
        ]
        playlist_content = generate_playlist(matching_channels)
        with open(f"output/playlists/{playlist}.m3u", "w", encoding="utf-8") as f:
            f.write(playlist_content)
        print(f"Generated output/playlists/{playlist}.m3u")

    print("Finished IPTV playlist generation.")


def generate_full_iptv_playlist():
    with open("data/iptv_database.json", "r", encoding="utf-8") as f:
        playlist_data = json.load(f)

    full_playlist_data = []
    seen_channel_urls = set()
    for channel in playlist_data:
        if not len(channel["commented_urls"]):
            full_playlist_data.append(channel)
        else:
            urls = []
            if channel["url"] not in seen_channel_urls:
                urls.append(channel["url"])
                seen_channel_urls.add(channel["url"])

            for commented_url in channel["commented_urls"]:
                url = re.sub(r"^#\s*", "", commented_url)
                if url not in seen_channel_urls:
                    urls.append(url)
                    seen_channel_urls.add(url)

            for enum, url in enumerate(urls, start=1):
                new_channel = channel.copy()
                new_channel["url"] = url
                new_channel["tvg-name"] = f"{channel['tvg-name']} ({enum})"
                new_channel["name"] = f"{channel['name']} ({enum})"
                new_channel["commented_urls"] = []
                full_playlist_data.append(new_channel)

    playlist_content = generate_playlist(
        natsorted(full_playlist_data, key=lambda ch: ch["name"].casefold())
    )
    with open("output/playlists/playlist_all.m3u", "w", encoding="utf-8") as f:
        f.write(playlist_content)
    print("Generated output/playlists/playlist_all.m3u")


def generate_youtube_playlist():
    """
    Updates the YouTube streams and generates the corresponding M3U playlist.
    """
    update_stream_urls()
    write_playlist()


def generate_youtube_epg():
    """
    Generates the EPG for the YouTube streams.
    """
    write_youtube_epg_file()


if __name__ == "__main__":
    check_streams()
    generate_iptv_playlists()
    generate_full_iptv_playlist()
    # generate_youtube_playlist()
    # generate_youtube_epg()
