import json
import re

from natsort import natsorted


def parse_playlist(playlist_content: str) -> list[dict]:
    """
    Parses the content of an M3U playlist, including commented-out URLs,
    into a list of dictionaries.

    Args:
        playlist_content: A string containing the M3U playlist data.

    Returns:
        A list of dictionaries, where each dictionary represents a channel
        and includes a list of any commented-out URLs.
    """
    # Split the playlist into chunks, with each chunk starting with #EXTINF
    # The (?=...) is a positive lookahead to keep the delimiter
    chunks = re.split(r"(?=#EXTINF)", playlist_content)
    playlist_data = []

    extinf_pattern = re.compile(r"#EXTINF:-1 (.*),(.*)")
    attributes_pattern = re.compile(r'(\S+?)="(.*?)"')

    for chunk in chunks:
        if not chunk.strip() or not chunk.startswith("#EXTINF"):
            continue

        lines = [line.strip() for line in chunk.strip().split("\n") if line.strip()]

        # The first line is always the #EXTINF metadata
        extinf_line = lines[0]
        match = extinf_pattern.match(extinf_line)

        if not match:
            continue

        attributes_str = match.group(1).strip()
        channel_name = match.group(2).strip()
        attributes = dict(attributes_pattern.findall(attributes_str))

        channel_info = {
            "tvg-id": attributes.get("tvg-id"),
            "tvg-name": attributes.get("tvg-name"),
            "tvg-logo": attributes.get("tvg-logo"),
            "group-title": attributes.get("group-title"),
            "name": channel_name,
            "url": None,
            "commented_urls": [],
        }

        # Process the subsequent lines for URLs
        for i in range(1, len(lines)):
            line = lines[i]
            if line.startswith("#"):
                # It's a commented line, store it
                channel_info["commented_urls"].append(line)
            else:
                # The first non-commented line is the active URL
                channel_info["url"] = line

        playlist_data.append(channel_info)

    return playlist_data


def generate_playlist(playlist_data: list[dict]) -> str:
    """
    Generates an M3U playlist string from a list of channel dictionaries,
    including commented-out URLs.

    Args:
        playlist_data: A list of dictionaries representing channels.
                       Each dict can contain a 'commented_urls' list.

    Returns:
        A string containing the formatted M3U playlist.
    """
    # Start with the M3U header
    playlist_parts = [
        '#EXTM3U url-tvg="https://epgshare01.online/epgshare01/epg_ripper_US2.xml.gz"'
    ]

    # Add a blank line if the source file had one (optional, for style)
    if any("url-tvg" in k for d in playlist_data for k in d):
        playlist_parts[0] += ' url-tvg=""'  # Replicate original header if needed

    playlist_parts.append("")

    for channel_info in playlist_data:
        attributes = []
        # Dynamically build attributes string from available keys
        for key in ["tvg-id", "tvg-name", "tvg-logo", "group-title"]:
            if channel_info.get(key):
                attributes.append(f'{key}="{channel_info[key]}"')

        attributes_str = " ".join(attributes)

        # Create the #EXTINF line
        extinf_line = f'#EXTINF:-1 {attributes_str},{channel_info.get("name", "")}'
        playlist_parts.append(extinf_line)

        # Add any commented URLs
        if channel_info.get("commented_urls"):
            for commented_url in channel_info["commented_urls"]:
                playlist_parts.append(commented_url)

        # Add the active URL
        if channel_info.get("url"):
            playlist_parts.append(channel_info["url"])

        playlist_parts.append("")

    return "\n".join(playlist_parts)


def json_to_m3u():
    with open("playlist_new_epg.json", "r", encoding="utf-8") as f:
        playlist_data = json.load(f)

    playlist_content = generate_playlist(
        natsorted(playlist_data, key=lambda ch: ch["name"].casefold())
    )
    with open("playlist_new_epg.m3u", "w", encoding="utf-8") as f:
        f.write(playlist_content)


if __name__ == "__main__":
    json_to_m3u()
