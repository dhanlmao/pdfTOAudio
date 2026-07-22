"""
PDF to Audiobook Converter — modern edition
Uses Microsoft Edge's neural TTS voices (via edge-tts) instead of robotic espeak.
"""

import asyncio
import os
import re
from tkinter.filedialog import askopenfilename

import edge_tts
import pypdf

# --- Config ---------------------------------------------------------------

# Some natural-sounding options. Run `edge-tts --list-voices` to see all.
VOICE = "en-US-AriaNeural"      # warm, natural US female voice
# Other good ones to try:
# "en-US-GuyNeural"        - natural US male voice
# "en-GB-SoniaNeural"      - natural British female voice
# "en-GB-RyanNeural"       - natural British male voice
# "en-US-AndrewNeural"     - newer, very conversational US male voice

RATE = "+0%"    # e.g. "+15%" to speak faster, "-10%" to slow down


# --- PDF extraction ---------------------------------------------------------

def extract_text(pdf_path: str) -> str:
    reader = pypdf.PdfReader(pdf_path)
    chunks = []
    for page in reader.pages:
        text = page.extract_text() or ""
        chunks.append(text)
    full_text = "\n".join(chunks)

    # Clean up common PDF extraction artifacts: hyphenated line-breaks,
    # stray newlines mid-sentence, excessive whitespace.
    full_text = re.sub(r"-\n", "", full_text)
    full_text = re.sub(r"\s+", " ", full_text)
    return full_text.strip()


# --- TTS generation ---------------------------------------------------------

async def generate_audio(text: str, output_path: str, voice: str = VOICE, rate: str = RATE):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)


def chunk_text(text: str, max_chars: int = 8000):
    """Edge-tts handles long text fine, but chunking avoids timeouts on huge PDFs."""
    for i in range(0, len(text), max_chars):
        yield text[i:i + max_chars]


async def convert_pdf_to_audiobook(pdf_path: str, output_dir: str = "."):
    print(f"Reading: {pdf_path}")
    text = extract_text(pdf_path)

    if not text:
        print("No extractable text found in this PDF (it may be scanned/image-based).")
        return

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    chunks = list(chunk_text(text))

    if len(chunks) == 1:
        output_path = os.path.join(output_dir, f"{base_name}.mp3")
        print(f"Generating audio -> {output_path}")
        await generate_audio(chunks[0], output_path)
        print("Done.")
    else:
        print(f"Large PDF detected — splitting into {len(chunks)} parts.")
        for idx, chunk in enumerate(chunks, start=1):
            output_path = os.path.join(output_dir, f"{base_name}_part{idx}.mp3")
            print(f"Generating part {idx}/{len(chunks)} -> {output_path}")
            await generate_audio(chunk, output_path)
        print("Done. You can merge the parts with ffmpeg if you want a single file.")


# --- Entry point -------------------------------------------------------------

def main():
    pdf_path = askopenfilename(
        title="Select a PDF to convert",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not pdf_path:
        print("No file selected.")
        return

    asyncio.run(convert_pdf_to_audiobook(pdf_path))


if __name__ == "__main__":
    main()
