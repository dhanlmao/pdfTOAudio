# PDF → Audiobook Converter

Convert any text-based PDF into a natural-sounding audiobook, with a simple
desktop GUI to convert, play, pause, and save the result.

Instead of robotic offline TTS (espeak), this uses **Microsoft Edge's neural
voices** via [`edge-tts`](https://github.com/rany2/edge-tts) — free, no API
key required, and genuinely natural-sounding.

## Features

- Simple desktop GUI (Tkinter) — no command-line arguments needed
- Natural neural TTS voices (US/UK, male/female)
- Play, pause, and stop playback right inside the app
- Save the generated MP3 anywhere you like
- Cleans up common PDF text-extraction artifacts (hyphenated line breaks, stray whitespace)

## Requirements

- Python 3.10+
- A PDF with selectable/extractable text (scanned/image-only PDFs won't work — see [Limitations](#limitations))

## Installation

```bash
pip install edge-tts pypdf pygame --break-system-packages
```

> `--break-system-packages` is needed on Arch/Omarchy and other distros that
> mark the system Python as externally managed. If you're using a virtual
> environment instead, you can drop that flag.

You'll also need Tk support for Python itself:

**Arch / Omarchy:**
```bash
sudo pacman -S tk
```

**Debian / Ubuntu:**
```bash
sudo apt install python3-tk
```

## Usage

```bash
python3 main.py
```

1. Click **Choose PDF** and select your file.
2. Pick a voice from the dropdown.
3. Click **Convert to Audiobook** and wait for it to finish (progress bar will spin).
4. Use **▶ Play / ⏸ Pause / ⏹ Stop** to listen right in the app.
5. Click **Save MP3 As...** to copy the file wherever you want. Otherwise, it's
   saved automatically to your home directory as `<filename>_audiobook.mp3`.

## Available Voices

| Label                              | Voice ID              |
|-------------------------------------|------------------------|
| Aria (US, Female)                   | `en-US-AriaNeural`     |
| Andrew (US, Male, conversational)    | `en-US-AndrewNeural`   |
| Guy (US, Male)                      | `en-US-GuyNeural`      |
| Sonia (UK, Female)                   | `en-GB-SoniaNeural`    |
| Ryan (UK, Male)                     | `en-GB-RyanNeural`     |

Want more options? Run:

```bash
edge-tts --list-voices
```

and add any voice ID you like to the `VOICES` dictionary at the top of `main.py`.

## Limitations

- **Scanned/image-based PDFs won't work** — text extraction relies on the PDF
  having actual selectable text, not just page images. For scanned documents,
  you'd need OCR first (e.g. `ocrmypdf`) before running this.
- **No seek/scrub bar yet** — playback is play/pause/stop only; you can't jump
  to a specific point in the audio.
- **Very large PDFs** may take a while to generate, since the whole document
  is sent through the TTS engine.
- Requires an internet connection, since `edge-tts` streams audio from
  Microsoft's TTS service (it's free, but not fully offline).

## Project Structure

```
.
├── main.py       # GUI app: PDF extraction, TTS generation, and playback
└── README.md
```

## Roadmap Ideas

- [ ] Seek/scrub bar with elapsed/total time
- [ ] Chapter/page-range selection before converting
- [ ] Adjustable speech rate slider in the UI
- [ ] Batch conversion for multiple PDFs at once
