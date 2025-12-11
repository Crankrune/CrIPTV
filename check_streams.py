import json
import subprocess
from copy import deepcopy
from typing import Any

with open("data/iptv_database_info.json", "r", encoding="utf-8") as f:
    json_db: list[dict[str, str | list[str]]] = json.load(f)


def get_stream_info(url: str) -> dict:
    # ffprobe
    p = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_entries",
            "stream=width,height,avg_frame_rate,bit_rate,codec_name:format=duration,bit_rate",
            url,
        ],
        stdout=subprocess.PIPE,
    )
    return json.loads(p.stdout.decode("utf-8"))


def get_best_stream(data: dict) -> dict[str, Any] | None:
    """
    Parses ffprobe output to find the single highest quality video stream.
    Prioritizes Resolution (Height), then Framerate (FPS).
    """
    candidates = []

    # Iterate through the flat 'streams' list
    for stream in data.get("streams", []):
        # Skip streams that aren't video (missing dimensions)
        if "width" not in stream or "height" not in stream:
            continue

        # Parse FPS fraction (e.g., "60/1" -> 60.0)
        fps_str = stream.get("avg_frame_rate", "0/0")
        fps = 0.0
        try:
            if "/" in fps_str:
                num, den = map(int, fps_str.split("/"))
                if den > 0:
                    fps = num / den
        except (ValueError, TypeError):
            pass

        candidates.append(
            {
                "width": int(stream["width"]),
                "height": int(stream["height"]),
                "fps": round(fps, 2),
                "codec": stream.get("codec_name", "unknown"),
                # Include bitrate if present, but don't rely on it for sorting
                # as it is often missing in HLS manifests
                "bitrate": stream.get("bit_rate", None),
            }
        )

    if not candidates:
        return None

    # Sort logic:
    # 1. Height (Resolution)
    # 2. FPS (Smoother motion)
    # We use 'max' with a tuple key to handle the sorting automatically
    best_stream = max(candidates, key=lambda x: (x["height"], x["fps"]))

    return best_stream


def process_channels(
    channels: list[dict[str, str | int | list[str]]],
    output: str = "data/iptv_database_info.json",
) -> None:
    updated_channels: list[dict[str, str | int | list[str] | bool]] = []
    for channel in channels:
        stream_url: str = channel["url"]
        channel_info: dict = deepcopy(channel)
        stream_info: dict = get_stream_info(stream_url)
        main_stream: dict = get_best_stream(stream_info)

        if main_stream is not None:
            channel_info["width"] = main_stream.get("width", 0)
            channel_info["height"] = main_stream.get("height", 0)
            channel_info["fps"] = main_stream.get("fps", 0)
            channel_info["codec"] = main_stream.get("codec", "unknown")
            channel_info["bitrate"] = main_stream.get("bitrate", 0)
            channel_info["working"] = True
        else:
            channel_info["working"] = False

        updated_channels.append(channel_info)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(updated_channels, f, indent=2)


# url = "http://fl1.moveonjoy.com/MLB_1/index.m3u8"
# stream_info = get_stream_info(url)
# main_stream = get_best_stream(stream_info)
# print(url, main_stream, sep="\n")


def main():
    process_channels(json_db)


if __name__ == "__main__":
    main()
