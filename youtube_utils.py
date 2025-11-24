import json
import subprocess
import time

from m3u_utils import generate_playlist


def get_youtube_stream_url(url: str) -> str:
    p = subprocess.run(
        ["yt-dlp", "--cookies-from-browser", "firefox", "-g", url],
        stdout=subprocess.PIPE,
    )
    return p.stdout.decode("utf-8").strip("\n")


def update_stream_urls():
    with open("data/youtube_channels.json", "r", encoding="utf-8") as f:
        data_template = json.load(f)

    updated_data = []
    for item in data_template:
        url = get_youtube_stream_url(
            f"https://www.youtube.com/watch?v={item['tvg-id']}"
        )
        if not url:
            print(f"[{item['tvg-id']}]", item["name"], "not found")
            continue
        item["url"] = url
        updated_data.append(item)
        time.sleep(3)

    with open("data/youtube_channels.json", "w", encoding="utf-8") as f:
        json.dump(updated_data, f, indent=2)


def write_playlist():
    with open("output/playlists/playlist_youtube.m3u", "w", encoding="utf-8") as fl:
        with open("data/youtube_channels.json", "r", encoding="utf-8") as f:
            streams_data = json.load(f)
        fl.write(generate_playlist(streams_data))


if __name__ == "__main__":
    update_stream_urls()
    write_playlist()
