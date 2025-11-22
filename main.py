from dummy_epg_gen import write_epg
from json_to_m3u import json_to_m3u
from youtube_streams_update import youtube_streams_update
from youtube_to_m3u import write_playlist

if __name__ == "__main__":
    json_to_m3u()
    youtube_streams_update()
    write_playlist()
    write_epg()
