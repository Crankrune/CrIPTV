import json
import subprocess
import time


def link_to_m3u8(url: str) -> str:
    p = subprocess.run(
        ["yt-dlp", "--cookies-from-browser", "firefox", "-g", url],
        stdout=subprocess.PIPE,
    )
    return p.stdout.decode("utf-8").strip("\n")


def youtube_streams_update():
    with open("youtube_streams.json", "r", encoding="utf-8") as f:
        data_template = json.load(f)

    updated_data = []
    for item in data_template:
        url = link_to_m3u8(f"https://www.youtube.com/watch?v={item['tvg-id']}")
        if not url:
            print(f"[{item['tvg-id']}]", item["name"], "not found")
            continue
        item["url"] = url
        updated_data.append(item)
        time.sleep(3)

    with open("youtube_streams.json", "w", encoding="utf-8") as f:
        json.dump(updated_data, f, indent=2)


if __name__ == "__main__":
    youtube_streams_update()
