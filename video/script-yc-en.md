# Synapses launch film, YC style: English voice-over script

Same timing as `script-yc.md` (the French script). The app shots are filmed on the English interface: `node record.js --en` (clips in `clips-en/`).
Voice: Vincent’s, cloned locally by Chatterbox from his French sample (the model carries a voice across languages):
  ~/.local/share/synapses-voix/bin/python video/voix-clone.py voix-vincent.m4a --en   → out/voix-yc-en.m4a
Music: the same Pixabay track as the French film (see `script-yc.md`): `MUSIQUE=musique-pixabay-yc.wav sh mixer.sh yc-en`.
Images: `node render.js 169 out/bande-son-yc-en.m4a --film yc --en`.

| Start | End | On screen | Voice-over |
|---|---|---|---|
| 0:00,0 | 0:03,6 | Title: SYNAPSES, huge, over the network | I’m Vincent, and I built Synapses. |
| 0:03,6 | 0:08,4 | Giant words: 843 contacts, no big picture | On LinkedIn, you have hundreds of contacts, and no big picture. |
| 0:08,4 | 0:13,6 | Scrolling wall of contacts: “An endless list.” | Just an endless list. Who do you know, and where? Impossible to tell. |
| 0:13,6 | 0:17,0 | Logo Synapses | Synapses turns it into a map. |
| 0:17,0 | 0:22,6 | 1. Drop | Drop your LinkedIn export, and your network appears. |
| 0:22,6 | 0:28,2 | 2. Group | Group it by industry, company, function or seniority. |
| 0:28,2 | 0:34,0 | 3. Dive in | One click on an industry: the people closest to you first. |
| 0:34,0 | 0:41,0 | 4. Way in | Got a company in mind? Synapses shows you who can open the door. |
| 0:41,0 | 0:46,4 | 5. By company | And you finally see where your network clusters. |
| 0:46,4 | 0:51,4 | Cadenas: 100 % in your browser | Everything happens in your browser: your file never leaves it. |
| 0:51,4 | 0:57,4 | End: URL | Synapses. Free, no sign-up. Try it on your own network. |
