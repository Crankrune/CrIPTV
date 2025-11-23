from dummy_epg_gen import write_epg
from json_to_m3u import json_to_m3u, write_specific_playlists
from youtube_streams_update import youtube_streams_update
from youtube_to_m3u import write_playlist

if __name__ == "__main__":
    json_to_m3u()
    write_specific_playlists()
    youtube_streams_update()
    write_playlist()
    write_epg()
