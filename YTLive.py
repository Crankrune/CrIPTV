import os
import re
import time
from pprint import pprint

import yt_dlp


def pause() -> None:
    input("Press Enter to continue...")
    return


def is_live_ydl(video_id: str, debug: bool = False) -> bool:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
        "allow_unplayable_formats": True,
        "extractor_args": {
            "youtube": {"player_client": ["android_testsuite", "android", "web"]}
        },
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}", download=False
            )
    except Exception:
        return False

    live_status = info.get("live_status")
    is_live_flag = info.get("is_live")
    was_live_flag = info.get("was_live")
    viewers = info.get("concurrent_viewers")

    if debug:
        print(
            f"{video_id}: live_status={live_status}, is_live={is_live_flag}, was_live={was_live_flag}, viewers={viewers}"
        )

    # definitive live
    if live_status == "is_live":
        return True
    if is_live_flag is True:
        return True
    if viewers is not None:
        return True  # only present on active lives

    # explicitly not live
    return False


def get_live_from_url(video_url: str) -> list[dict]:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "format": "best",
        "ignoreerrors": True,
        "allow_unplayable_formats": True,
        "extractor_args": {
            "youtube": {"player_client": ["android_testsuite", "android", "web"]}
        },
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        e = ydl.extract_info(video_url, download=False)

    if not e or not (
        e.get("live_status") == "is_live"
        or e.get("is_live") is True
        or e.get("concurrent_viewers") is not None
    ):
        return []

    thumbs = e.get("thumbnails") or []
    best_thumb = e.get("thumbnail")
    if not best_thumb and thumbs:
        best_thumb = max(thumbs, key=lambda t: t.get("width", 0)).get("url")

    direct_url = e.get("url")
    if not direct_url:
        formats = [f for f in e.get("formats", []) if f.get("url")]
        if formats:
            best = max(formats, key=lambda f: (f.get("height") or 0, f.get("tbr") or 0))
            direct_url = best["url"]

    vid_id = e.get("id")
    return [
        {
            "id": vid_id,
            "url": (
                f"https://www.youtube.com/watch?v={vid_id}"
                if vid_id
                else e.get("webpage_url")
            ),
            "title": e.get("title"),
            "fulltitle": e.get("fulltitle"),
            "uploader": e.get("uploader"),
            "uploader_id": e.get("uploader_id"),
            "uploader_url": e.get("uploader_url"),
            "channel": e.get("channel"),
            "channel_id": e.get("channel_id"),
            "channel_url": e.get("channel_url"),
            "webpage_url": e.get("webpage_url"),
            "thumbnail": best_thumb,
            "direct_url": direct_url,
            "upload_date": e.get("upload_date"),
            "live_status": e.get("live_status"),
            "is_live": e.get("is_live"),
            "was_live": e.get("was_live"),
            "concurrent_viewers": e.get("concurrent_viewers"),
            "availability": e.get("availability"),
            "release_timestamp": e.get("release_timestamp"),
            "channel_follower_count": e.get("channel_follower_count"),
            "categories": e.get("categories"),
            "tags": e.get("tags"),
        }
    ]


def get_live_streams(channel: str) -> list[dict]:
    if channel.startswith("http"):
        channel_url = channel.rstrip("/")
    else:
        handle = channel if channel.startswith("@") else f"@{channel}"
        channel_url = f"https://www.youtube.com/{handle}"

    list_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": True,
        "playlistend": 20,
        "ignoreerrors": True,
    }
    with yt_dlp.YoutubeDL(list_opts) as ydl:
        info = ydl.extract_info(channel_url + "/streams", download=False)

    lives = []
    for e in info.get("entries") or []:
        if not e:
            continue
        vid_id = e.get("id") or e.get("url")
        if not vid_id:
            continue
        video_url = (
            f"https://www.youtube.com/watch?v={vid_id}" if len(vid_id) == 11 else vid_id
        )
        lives.extend(get_live_from_url(video_url))

    return lives


def print_live_streams(streams: list[dict]) -> None:
    if not streams:
        print("No live streams found.")
        return

    for stream in streams:
        title = stream.get("title") or "(no title)"
        print(f"{title} | {stream['url']}")


def clean_titles(title: str) -> str:
    clean_title: str = re.sub("^(LIVE:\s|LIVE\s?NEWS:\s)", "", title, flags=re.I)
    return clean_title


def lives_to_m3u_dict(lives: list[dict]) -> dict[str, str]:
    m3u_dicts: list[dict] = []
    for live in lives:
        m3u_dicts.append(
            {
                "tvg-name": clean_titles(
                    live.get("fulltitle") or live.get("title") or ""
                ),
                "tvg-id": live.get("id") or "",
                "tvg-logo": live.get("thumbnail") or "",
                "name": live.get("fulltitle") or "",
                "url": live.get("direct_url") or live.get("url") or "",
                "group-title": live.get("tags")[0] if len(live.get("tags")) else "",
                "channel": live.get("channel") or "",
            }
        )
    m3u_dicts.sort(key=lambda x: (x["channel"], x["name"]))
    return m3u_dicts


def dicts_to_m3u(m3u_dicts: list[dict], epg: str | None = None) -> str:
    epg: str = (
        epg
        or "https://github.com/Crankrune/CrIPTV/raw/refs/heads/main/output/youtube_epg.xml"
    )
    extm3u: str = f'#EXTM3U url-tvg="{epg}"\n'
    lines: list[str] = [extm3u]

    for m3u_dict in m3u_dicts:
        line: str = (
            f'#EXTINF:-1 tvg-id="{m3u_dict["tvg-id"]}" tvg-name="{m3u_dict["tvg-name"]}" tvg-logo="{m3u_dict["tvg-logo"]}" group-title="{m3u_dict["group-title"]}",{m3u_dict["name"]}\n'
        )
        line += m3u_dict["url"] + "\n"
        lines.append(line)

    m3u: str = "\n".join(lines)
    return m3u


def channels_to_m3u(
    channels: list[str] | None = None, links: list[str] | None = None
) -> str:
    lives: list[dict] = []

    if channels:
        for channel in channels:
            lives.extend(get_live_streams(channel))

    if links:
        for link in links:
            lives.extend(get_live_from_url(link))

    m3u_dicts: list[dict] = lives_to_m3u_dict(lives)
    m3u: str = dicts_to_m3u(m3u_dicts)

    return m3u


CHANNELS: list[str] = [
    "@LofiGirl",
    "@NBCNews",
    "@CBSNews",
    "@ABCNews",
    "@LiveNowFOX",
]

LINKS: list[str] = [
    "https://www.youtube.com/watch?v=8rTTEMdMh8Q",
]


def main() -> None:
    start: float = time.perf_counter()
    m3u: str = channels_to_m3u(CHANNELS, LINKS)
    os.makedirs("output/playlists", exist_ok=True)
    with open("youtube.m3u", "w", encoding="utf-8") as f:
        f.write(m3u)

    end: float = time.perf_counter()
    m, s = divmod(end - start, 60)
    print(f"Done in {m:.0f}m{s:.2f}s")


if __name__ == "__main__":
    main()
