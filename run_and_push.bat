@echo off
python main.py

git add .
git add playlist_new_epg.m3u
git commit -m "update"
git push

pause