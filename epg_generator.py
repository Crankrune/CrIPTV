import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from xml.dom import minidom


def create_epg_from_m3u(
    m3u_content: str, days_to_generate: int = 2, block_hours: int = 1
) -> str:
    """
    Parses M3U playlist content and creates an EPG XML with hourly program blocks
    starting from the current time.
    """
    root = ET.Element("tv")
    root.set("generator-info-name", "Gemini-EPG-Generator")

    # Calculate time range
    # Round down to the nearest hour for a cleaner look
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

    # Total number of blocks to generate
    total_hours = days_to_generate * 24
    num_blocks = int(total_hours / block_hours)

    processed_ids = set()
    lines = m3u_content.strip().split("\n")

    for line in lines:
        if line.startswith("#EXTINF"):
            # Extract the tvg-id
            tvg_id_match = re.search(r'tvg-id="([^"]*)"', line)

            # If no tvg-id exists, we can't link EPG to channel, so skip or generate a fake one
            # Here we skip to be safe, but you could use the channel name as ID
            if not tvg_id_match:
                continue

            channel_id = tvg_id_match.group(1)
            if not channel_id:
                continue

            # Ensure each channel is only added once
            if channel_id in processed_ids:
                continue
            processed_ids.add(channel_id)

            # The channel name is the text after the last comma
            channel_name = line.split(",")[-1].strip()

            # 1. Create the <channel> element
            channel_el = ET.SubElement(root, "channel")
            channel_el.set("id", channel_id)
            display_name_el = ET.SubElement(channel_el, "display-name")
            display_name_el.text = channel_name

            # 2. Create multiple <programme> blocks
            for i in range(num_blocks):
                # Calculate start and stop for this specific block
                start_dt = now + timedelta(hours=i * block_hours)
                stop_dt = start_dt + timedelta(hours=block_hours)

                # XMLTV Format: YYYYMMDDhhmmss +0000
                fmt = "%Y%m%d%H%M%S +0000"

                programme_el = ET.SubElement(root, "programme")
                programme_el.set("start", start_dt.strftime(fmt))
                programme_el.set("stop", stop_dt.strftime(fmt))
                programme_el.set("channel", channel_id)

                title_el = ET.SubElement(programme_el, "title")
                title_el.set("lang", "en")
                # Display channel name as the show title
                title_el.text = channel_name

                # Optional: Add description so it looks populated
                desc_el = ET.SubElement(programme_el, "desc")
                desc_el.set("lang", "en")
                desc_el.text = f"Continuous streaming of {channel_name}"

    # Convert the XML tree to a formatted string
    # (minidom is slow for massive files, but fine for typical usage)
    xml_str = ET.tostring(root, "utf-8")
    dom = minidom.parseString(xml_str)
    return dom.toprettyxml(indent="  ")


def write_youtube_epg_file():
    try:
        with open(
            "output/playlists/playlist_youtube.m3u", "r", encoding="utf-8"
        ) as m3u_file:
            m3u_content = m3u_file.read()

        epg_xml = create_epg_from_m3u(m3u_content)

        with open("output/youtube_epg.xml", "w", encoding="utf-8") as f:
            f.write(epg_xml)

        print("EPG successfully generated.")
    except FileNotFoundError:
        print("Error: output/playlists/playlist_youtube.m3u not found.")


if __name__ == "__main__":
    write_youtube_epg_file()
