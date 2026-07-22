"""
PDF to Audiobook Converter — GUI edition
Converts PDFs to natural-sounding audio (via edge-tts) and plays them back
right inside the app, with play/pause/stop controls and a progress bar.
"""

import asyncio
import os
import re
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import edge_tts
import pygame
import pypdf

VOICES = {
    "Aria (US, Female)": "en-US-AriaNeural",
    "Andrew (US, Male, conversational)": "en-US-AndrewNeural",
    "Guy (US, Male)": "en-US-GuyNeural",
    "Sonia (UK, Female)": "en-GB-SoniaNeural",
    "Ryan (UK, Male)": "en-GB-RyanNeural",
}


# --- Core conversion logic ---------------------------------------------------

def extract_text(pdf_path: str) -> str:
    reader = pypdf.PdfReader(pdf_path)
    chunks = [page.extract_text() or "" for page in reader.pages]
    full_text = "\n".join(chunks)
    full_text = re.sub(r"-\n", "", full_text)
    full_text = re.sub(r"\s+", " ", full_text)
    return full_text.strip()


async def generate_audio(text: str, output_path: str, voice: str, rate: str = "+0%"):
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(output_path)


# --- GUI ---------------------------------------------------------------------

class AudiobookApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF → Audiobook")
        self.geometry("520x360")
        self.resizable(False, False)

        pygame.mixer.init()

        self.pdf_path = None
        self.output_path = None
        self.is_playing = False
        self.is_paused = False

        self._build_ui()

    # -- UI construction --

    def _build_ui(self):
        pad = {"padx": 16, "pady": 8}

        # File selection
        file_frame = ttk.Frame(self)
        file_frame.pack(fill="x", **pad)

        self.file_label = ttk.Label(file_frame, text="No PDF selected", foreground="gray")
        self.file_label.pack(side="left", fill="x", expand=True)

        ttk.Button(file_frame, text="Choose PDF", command=self.choose_pdf).pack(side="right")

        # Voice selection
        voice_frame = ttk.Frame(self)
        voice_frame.pack(fill="x", **pad)

        ttk.Label(voice_frame, text="Voice:").pack(side="left")

        self.voice_var = tk.StringVar(value=list(VOICES.keys())[0])
        voice_dropdown = ttk.Combobox(
            voice_frame, textvariable=self.voice_var,
            values=list(VOICES.keys()), state="readonly", width=32
        )
        voice_dropdown.pack(side="right")

        # Convert button
        self.convert_btn = ttk.Button(self, text="Convert to Audiobook", command=self.start_conversion)
        self.convert_btn.pack(pady=12)

        # Progress bar
        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", padx=16)

        self.status_label = ttk.Label(self, text="", foreground="gray")
        self.status_label.pack(pady=4)

        # Playback controls
        playback_frame = ttk.Frame(self)
        playback_frame.pack(pady=20)

        self.play_btn = ttk.Button(playback_frame, text="▶ Play", command=self.play_audio, state="disabled")
        self.play_btn.grid(row=0, column=0, padx=6)

        self.pause_btn = ttk.Button(playback_frame, text="⏸ Pause", command=self.pause_audio, state="disabled")
        self.pause_btn.grid(row=0, column=1, padx=6)

        self.stop_btn = ttk.Button(playback_frame, text="⏹ Stop", command=self.stop_audio, state="disabled")
        self.stop_btn.grid(row=0, column=2, padx=6)

        # Save-as button
        self.save_btn = ttk.Button(self, text="Save MP3 As...", command=self.save_as, state="disabled")
        self.save_btn.pack(pady=6)

    # -- File handling --

    def choose_pdf(self):
        path = filedialog.askopenfilename(
            title="Select a PDF", filetypes=[("PDF files", "*.pdf")]
        )
        if path:
            self.pdf_path = path
            self.file_label.config(text=os.path.basename(path), foreground="black")
            self._reset_playback_state()

    # -- Conversion --

    def start_conversion(self):
        if not self.pdf_path:
            messagebox.showwarning("No PDF", "Please choose a PDF first.")
            return

        self.convert_btn.config(state="disabled")
        self.progress.start(12)
        self.status_label.config(text="Extracting text and generating audio...")

        thread = threading.Thread(target=self._convert_worker, daemon=True)
        thread.start()

    def _convert_worker(self):
        try:
            text = extract_text(self.pdf_path)
            if not text:
                self.after(0, lambda: self._conversion_failed(
                    "No extractable text found (this PDF may be scanned/image-based)."
                ))
                return

            voice = VOICES[self.voice_var.get()]
            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            output_path = os.path.join(os.path.expanduser("~"), f"{base_name}_audiobook.mp3")

            asyncio.run(generate_audio(text, output_path, voice))

            self.output_path = output_path
            self.after(0, self._conversion_done)

        except Exception as e:
            self.after(0, lambda: self._conversion_failed(str(e)))

    def _conversion_done(self):
        self.progress.stop()
        self.convert_btn.config(state="normal")
        self.status_label.config(text=f"Saved: {os.path.basename(self.output_path)}")
        self.play_btn.config(state="normal")
        self.save_btn.config(state="normal")

    def _conversion_failed(self, message: str):
        self.progress.stop()
        self.convert_btn.config(state="normal")
        self.status_label.config(text="Conversion failed.")
        messagebox.showerror("Conversion failed", message)

    # -- Playback --

    def play_audio(self):
        if not self.output_path:
            return

        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            pygame.mixer.music.load(self.output_path)
            pygame.mixer.music.play()

        self.is_playing = True
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")

    def pause_audio(self):
        pygame.mixer.music.pause()
        self.is_paused = True

    def stop_audio(self):
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.pause_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")

    def _reset_playback_state(self):
        self.stop_audio()
        self.output_path = None
        self.play_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.status_label.config(text="")

    # -- Save --

    def save_as(self):
        if not self.output_path:
            return
        dest = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3")],
            initialfile=os.path.basename(self.output_path),
        )
        if dest:
            import shutil
            shutil.copy(self.output_path, dest)
            messagebox.showinfo("Saved", f"Saved to {dest}")


if __name__ == "__main__":
    app = AudiobookApp()
    app.mainloop()
