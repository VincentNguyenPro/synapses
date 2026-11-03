#!/bin/sh
# Mixe la voix off et la musique : la musique baisse automatiquement quand la voix parle (ducking).
# Usage : sh video/mixer.sh   → video/out/bande-son.m4a (à passer à render.js)
cd "$(dirname "$0")/out" || exit 1
ffmpeg -y -loglevel error -i voix-ia.m4a -i musique.wav -filter_complex "\
[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[v][sc];\
[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.42[m];\
[m][sc]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=450:makeup=1[md];\
[v][md]amix=inputs=2:normalize=0:duration=longest,loudnorm=I=-16:TP=-1.5:LRA=11[o]" \
  -map "[o]" -ar 48000 -c:a aac -b:a 192k bande-son.m4a && echo "→ video/out/bande-son.m4a"
