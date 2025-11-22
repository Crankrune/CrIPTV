import json
import re


def parse_playlist(playlist_content: str) -> list[dict]:
    """
    Parses the content of an M3U playlist into a list of dictionaries.

    Args:
        playlist_content: A string containing the M3U playlist data.

    Returns:
        A list of dictionaries, where each dictionary represents a channel
        with its metadata and URL.
    """
    # Regex to capture key-value pairs and the channel name from the #EXTINF line
    extinf_pattern = re.compile(r"#EXTINF:-1 (.*),(.*)")
    attributes_pattern = re.compile(r'(\S+?)="(.*?)"')

    lines = playlist_content.strip().split("\n")
    playlist_data = []

    # Iterate through the lines of the playlist
    for i in range(len(lines)):
        if lines[i].startswith("#EXTINF"):
            match = extinf_pattern.match(lines[i])
            if match:
                attributes_str = match.group(1).strip()
                channel_name = match.group(2).strip()

                attributes = dict(attributes_pattern.findall(attributes_str))

                # The URL is on the next line
                if i + 1 < len(lines):
                    url = lines[i + 1].strip()

                    channel_info = {
                        "tvg-id": attributes.get("tvg-id"),
                        "tvg-game": attributes.get("tvg-game"),
                        "tvg-logo": attributes.get("tvg-logo"),
                        "group-title": attributes.get("group-title"),
                        "name": channel_name,
                        "url": url,
                    }
                    playlist_data.append(channel_info)

    return playlist_data


def generate_playlist(playlist_data: list[dict]) -> str:
    """
    Generates an M3U playlist string from a list of channel dictionaries.

    Args:
        playlist_data: A list of dictionaries, where each dictionary
                       represents a channel.

    Returns:
        A string containing the formatted M3U playlist.
    """
    playlist_content = ['#EXTM3U url-tvg=""', ""]

    for channel_info in playlist_data:
        attributes = []
        if channel_info.get("tvg-id"):
            attributes.append(f'tvg-id="{channel_info["tvg-id"]}"')
        if channel_info.get("tvg-game"):
            attributes.append(f'tvg-game="{channel_info["tvg-game"]}"')
        if channel_info.get("tvg-logo"):
            attributes.append(f'tvg-logo="{channel_info["tvg-logo"]}"')
        if channel_info.get("group-title"):
            attributes.append(f'group-title="{channel_info["group-title"]}"')

        attributes_str = " ".join(attributes)

        extinf_line = f'#EXTINF:-1 {attributes_str},{channel_info.get("name", "")}'
        playlist_content.append(extinf_line)
        playlist_content.append(channel_info.get("url", ""))
        playlist_content.append("\n")

    return "\n".join(playlist_content)


def write_playlist():
    with open("youtube_auto.m3u", "w", encoding="utf-8") as fl:
        with open("youtube_streams.json", "r", encoding="utf-8") as f:
            streams_data = json.load(f)
        fl.write(generate_playlist(streams_data))


if __name__ == "__main__":
    write_playlist()
