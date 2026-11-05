#!/bin/sh
# Mixe la voix off et la musique : la musique baisse automatiquement quand la voix parle (ducking).
# Usage : sh video/mixer.sh [en|yc|yc-en]   → video/out/bande-son.m4a, bande-son-en.m4a (voix anglaise),
#   bande-son-yc.m4a (film de lancement : voix-yc.m4a + musique-yc.wav) ; à passer à render.js
cd "$(dirname "$0")/out" || exit 1
S=${1:+-$1}
case "$1" in
  yc*) VOIX=voix$S.m4a; MUS=musique-yc.wav; VOL=0.5 ;;
  *)   VOIX=voix-ia$S.m4a; MUS=musique.wav; VOL=0.42 ;;
esac
ffmpeg -y -loglevel error -i "$VOIX" -i "$MUS" -filter_complex "\
[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[v][sc];\
[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=$VOL[m];\
[m][sc]sidechaincompress=threshold=0.02:ratio=10:attack=15:release=450:makeup=1[md];\
[v][md]amix=inputs=2:normalize=0:duration=longest,loudnorm=I=-16:TP=-1.5:LRA=11[o]" \
  -map "[o]" -ar 48000 -c:a aac -b:a 192k bande-son$S.m4a && echo "→ video/out/bande-son$S.m4a"
