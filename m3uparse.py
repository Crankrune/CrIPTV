"""Parse and serialize M3U IPTV playlists."""

import re
import urllib.error
import urllib.request

ATTR_PATTERN = re.compile(r'([\w-]+)="((?:[^"\\]|\\.)*)"')

# Maps #EXTVLCOPT keys to the real HTTP header they represent, so
# check_status() can send requests the way the stream actually expects.
VLCOPT_HEADER_MAP = {
    "http-user-agent": "User-Agent",
    "http-referrer": "Referer",
    "http-referer": "Referer",
    "http-origin": "Origin",
    "http-cookie": "Cookie",
}


class Channel:
    """A single stream entry: its EXTINF attributes, any extra tag lines
    (EXTVLCOPT, etc.), and the stream URL."""

    def __init__(
        self,
        duration: float = -1.0,
        title: str = "",
        attrs: dict[str, str] | None = None,
        extra_lines: list[str] | None = None,
        url: str = "",
    ) -> None:
        self.duration = duration
        self.title = title
        self.attrs = attrs or {}
        self.extra_lines = extra_lines or []
        self.url = url

    @classmethod
    def from_extinf(cls, line: str) -> "Channel":
        """Build a Channel from a single #EXTINF line."""
        body = line[len("#EXTINF:") :]

        # Attribute values are always quoted, so the first comma outside
        # quotes ends the attribute section. Titles are unquoted and may
        # contain their own commas, so the last comma can't be the split
        # point.
        in_quotes = False
        split_at: int | None = None
        for i, char in enumerate(body):
            if char == '"':
                in_quotes = not in_quotes
            elif char == "," and not in_quotes:
                split_at = i
                break

        if split_at is None:
            head, title = body, ""
        else:
            head, title = body[:split_at], body[split_at + 1 :]

        duration_text, _, attr_text = head.partition(" ")
        attrs = dict(ATTR_PATTERN.findall(attr_text))

        try:
            duration = float(duration_text)
        except ValueError:
            duration = -1.0

        return cls(duration=duration, title=title.strip(), attrs=attrs)

    @property
    def is_radio(self) -> bool:
        return self.attrs.get("radio", "").lower() == "true"

    def stream_headers(self) -> dict[str, str]:
        """HTTP headers derived from this channel's #EXTVLCOPT lines."""
        headers: dict[str, str] = {}
        for line in self.extra_lines:
            if not line.upper().startswith("#EXTVLCOPT:"):
                continue
            key, _, value = line[len("#EXTVLCOPT:") :].partition("=")
            header_name = VLCOPT_HEADER_MAP.get(key.strip().lower())
            if header_name:
                headers[header_name] = value.strip()
        return headers

    def _format_duration(self) -> str:
        if self.duration == int(self.duration):
            return str(int(self.duration))
        return str(self.duration)

    def to_block(self) -> str:
        attr_text = " ".join(f'{key}="{value}"' for key, value in self.attrs.items())
        duration_str = self._format_duration()
        extinf_line = f"#EXTINF:{duration_str} {attr_text},{self.title}"

        lines = [extinf_line]
        lines.extend(self.extra_lines)
        lines.append(self.url)
        return "\n".join(lines)

    def check_status(self, timeout: float = 8.0) -> bool:
        """Return True if the stream URL responds without an error status.

        Applies any http-user-agent / http-referrer / http-origin /
        http-cookie headers found in this channel's #EXTVLCOPT lines,
        since many streams (e.g. PPV/sports origins) reject requests
        that don't include them.
        """
        headers = self.stream_headers()
        headers["Range"] = "bytes=0-1023"
        try:
            request = urllib.request.Request(self.url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.status < 400
        except (urllib.error.URLError, ValueError, TimeoutError):
            return False


class Playlist:
    """An M3U playlist: header attributes plus an ordered list of channels."""

    def __init__(
        self,
        channels: list[Channel] | None = None,
        header_attrs: dict[str, str] | None = None,
    ) -> None:
        self.channels = channels or []
        self.header_attrs = header_attrs or {}

    @classmethod
    def parse(cls, text: str) -> "Playlist":
        header_attrs: dict[str, str] = {}
        channels: list[Channel] = []
        pending: Channel | None = None

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith("#EXTM3U"):
                header_attrs = dict(ATTR_PATTERN.findall(line))
                continue

            if line.startswith("#EXTINF:"):
                pending = Channel.from_extinf(line)
                continue

            if line.startswith("#"):
                if pending is not None:
                    pending.extra_lines.append(line)
                continue

            if pending is not None:
                pending.url = line
                channels.append(pending)
                pending = None

        return cls(channels, header_attrs)

    def to_m3u(self) -> str:
        header_attr_text = " ".join(f'{k}="{v}"' for k, v in self.header_attrs.items())
        header = "#EXTM3U"
        if header_attr_text:
            header += f" {header_attr_text}"
        blocks = [channel.to_block() for channel in self.channels]
        return header + "\n" + "\n".join(blocks) + "\n"
