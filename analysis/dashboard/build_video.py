"""Build a narrated, captioned video from a slide deck PDF and per-slide narration.

Voice: Microsoft Edge neural text-to-speech through the `edge-tts` package (Jimmy's choice, 2026-11-09:
"use microsoft or elevenlabs or other free state of the art TTS"). It is free, needs no key, and reaches
speech.platform.bing.com through the session proxy. One request per slide, sequential, with retries;
sentence timing comes from the service's SentenceBoundary events and drives the captions and the SRT.
Synthesized audio is cached under data/cache/tts/ by voice, rate and text, so re-runs re-synthesize only
slides whose narration changed. `--no-tts` keeps the earlier captions-only behaviour.

Inputs: a deck PDF (rendered by LibreOffice) and a JSON with `slides[].narration` (one entry per slide).
Outputs, in --out-dir: <name>.mp4 (1280x720, H.264 + AAC), <name>.srt, <name>_narration_script.md.

  uv run python -m analysis.dashboard.build_video                 # the short overview
  uv run python -m analysis.dashboard.build_video --deck-pdf reports/deck/gp_rarelink_deep_dive.pdf \\
      --data analysis/dashboard/deep_dive_data.json --name gp_rarelink_deep_dive
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
W, H = 1280, 720
FPS = 24
LEAD = 0.6            # seconds a slide shows before its narration starts
TAIL = 0.6            # seconds of silence after a slide's narration
WORDS_PER_SECOND = 2.5
MIN_CAPTION = 2.0
MAX_CAPTION_CHARS = 120
BAND_H = 80          # caption strip below the slide; the slide is letterboxed above it so no content is hidden
SLIDE_H = H - BAND_H
SLIDE_W = round(SLIDE_H * 16 / 9)
FONT_CANDIDATES = ["/usr/share/fonts/opentype/inter/Inter-Medium.otf", "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
CACHE = ROOT / "data/cache/tts"
DEFAULT_VOICE = "en-US-AndrewMultilingualNeural"


def font(size):
    for f in FONT_CANDIDATES:
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def split_long(text: str, max_chars: int = MAX_CAPTION_CHARS) -> list[str]:
    """Split one long sentence into caption-sized pieces at clause boundaries (display only)."""
    if len(text) <= max_chars:
        return [text]
    parts, cur = [], ""
    for p in re.split(r"(?<=[;:,])\s+", text):
        if cur and len(cur) + 1 + len(p) > max_chars:
            parts.append(cur)
            cur = p
        else:
            cur = f"{cur} {p}".strip()
    if cur:
        parts.append(cur)
    return parts


def wrap(draw, text, fnt, max_width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        if draw.textlength(t, font=fnt) <= max_width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def frame(slide_png: Path, caption: str | None, out: Path, fnt):
    """The slide letterboxed above a fixed caption strip, so captions never cover slide content."""
    canvas = Image.new("RGB", (W, H), (11, 11, 11))
    slide = Image.open(slide_png).convert("RGB").resize((SLIDE_W, SLIDE_H), Image.LANCZOS)
    canvas.paste(slide, ((W - SLIDE_W) // 2, 0))
    if caption:
        draw = ImageDraw.Draw(canvas)
        f = fnt
        lines = wrap(draw, caption, f, W - 120)
        if len(lines) > 2:
            f = font(21)
            lines = wrap(draw, caption, f, W - 100)
        line_h = 34 if f is fnt else 29
        y = SLIDE_H + (BAND_H - line_h * len(lines)) // 2
        for ln in lines:
            tw = draw.textlength(ln, font=f)
            draw.text(((W - tw) / 2, y), ln, font=f, fill=(255, 255, 255))
            y += line_h
    canvas.save(out, "PNG")


def srt_time(t: float) -> str:
    h, rem = divmod(max(0.0, t), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def ffprobe_duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip()
    return float(out)


# ------------------------------------------------------------------------------------------------------- TTS
async def _synthesize(text: str, voice: str, rate: str, mp3: Path, meta: Path):
    import edge_tts  # imported here so --no-tts works without the package

    last = None
    for attempt in range(6):
        try:
            comm = edge_tts.Communicate(text, voice, rate=rate, proxy=os.environ.get("HTTPS_PROXY"))
            audio, bounds = b"", []
            async for ch in comm.stream():
                if ch["type"] == "audio":
                    audio += ch["data"]
                elif ch["type"] in ("SentenceBoundary", "WordBoundary"):
                    bounds.append({"type": ch["type"], "offset": ch["offset"] / 1e7, "duration": ch["duration"] / 1e7, "text": ch["text"]})
            if not audio:
                raise RuntimeError("empty audio")
            mp3.write_bytes(audio)
            meta.write_text(json.dumps({"voice": voice, "rate": rate, "text": text, "boundaries": bounds}, indent=0))
            return
        except Exception as e:  # noqa: BLE001 - the service refuses some requests at random; retry
            last = e
            await asyncio.sleep(2 + 3 * attempt)
    raise SystemExit(f"text-to-speech failed after 6 attempts: {type(last).__name__}: {last}")


def tts(text: str, voice: str, rate: str) -> tuple[Path, list[dict]]:
    CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(f"{voice}|{rate}|{text}".encode()).hexdigest()[:20]
    mp3, meta = CACHE / f"{key}.mp3", CACHE / f"{key}.json"
    if not (mp3.exists() and meta.exists()):
        asyncio.run(_synthesize(text, voice, rate, mp3, meta))
    return mp3, json.loads(meta.read_text())["boundaries"]


def caption_times(text: str, bounds: list[dict], audio_dur: float) -> list[tuple[float, float, str]]:
    """(start, end, caption) within the slide's audio, from sentence boundaries; proportional fallback."""
    sents = sentences(text)
    sb = [b for b in bounds if b["type"] == "SentenceBoundary"]
    out = []
    if len(sb) == len(sents) and sb:
        for b in sb:
            out.append((b["offset"], min(audio_dur, b["offset"] + b["duration"]), b["text"]))
    else:
        total_words = sum(len(s.split()) for s in sents) or 1
        t = 0.0
        for s in sents:
            d = audio_dur * len(s.split()) / total_words
            out.append((t, t + d, s))
            t += d
    # split captions that are too long to read, proportionally by characters
    final = []
    for start, end, s in out:
        pieces = split_long(s)
        if len(pieces) == 1:
            final.append((start, end, s))
            continue
        total = sum(len(p) for p in pieces)
        t = start
        for p in pieces:
            d = (end - start) * len(p) / total
            final.append((t, t + d, p))
            t += d
    return final


# ------------------------------------------------------------------------------------------------------ build
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--deck-pdf", default="reports/deck/gp_rarelink_overview.pdf")
    ap.add_argument("--data", default="analysis/dashboard/deck_data.json")
    ap.add_argument("--out-dir", default="reports/video")
    ap.add_argument("--name", default="gp_rarelink_overview")
    ap.add_argument("--voice", default=DEFAULT_VOICE)
    ap.add_argument("--rate", default="+0%", help="edge-tts rate, e.g. +5%%")
    ap.add_argument("--no-tts", action="store_true", help="captions only, silent track (the earlier behaviour)")
    ap.add_argument("--crf", type=int, default=23, help="x264 quality (higher = smaller file); 26 is fine for static slides")
    a = ap.parse_args(argv)
    deck_pdf, data_path, out_dir = ROOT / a.deck_pdf, ROOT / a.data, ROOT / a.out_dir
    data = json.loads(data_path.read_text())
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="gp_video_"))
    subprocess.run(["pdftoppm", "-png", "-scale-to-x", str(W), "-scale-to-y", str(H), str(deck_pdf), str(tmp / "slide")], check=True)
    slides = sorted(tmp.glob("slide-*.png"))
    if len(slides) != len(data["slides"]):
        raise SystemExit(f"{len(slides)} slide images but {len(data['slides'])} narration entries")
    fnt = font(25)
    frames: list[tuple[Path, float]] = []   # (png, seconds)
    audio_parts: list[Path] = []
    srt, script = [], [f"# Narration script: {data.get('title', a.name)}\n",
                       f"*Generated {data['date']} from `{data_path.relative_to(ROOT)}`. " + ("Voice: Microsoft Edge neural TTS, " + a.voice + ". " if not a.no_tts else "Captions only; no voice track. ") + "Timecodes are the video's.*\n"]
    t, n, k = 0.0, 0, 0

    def add_frame(png, caption, dur):
        nonlocal n
        if dur <= 0.01:
            return
        f = tmp / f"f{n:05d}.png"
        frame(png, caption, f, fnt)
        frames.append((f, dur))
        n += 1

    for i, (png, sl) in enumerate(zip(slides, data["slides"]), start=1):
        text = re.sub(r"\s+", " ", sl["narration"]).strip()
        start_t = t
        if a.no_tts:
            add_frame(png, None, LEAD)
            t += LEAD
            for s in sentences(text):
                for piece in split_long(s):
                    dur = max(MIN_CAPTION, len(piece.split()) / WORDS_PER_SECOND + 0.35)
                    add_frame(png, piece, dur)
                    k += 1
                    srt.append(f"{k}\n{srt_time(t)} --> {srt_time(t + dur)}\n{piece}\n")
                    t += dur
            add_frame(png, None, TAIL)
            t += TAIL
        else:
            mp3, bounds = tts(text, a.voice, a.rate)
            wav = tmp / f"a{i:03d}.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-af", f"adelay={int(LEAD * 1000)}|{int(LEAD * 1000)},apad=pad_dur={TAIL}",
                            "-ar", "24000", "-ac", "1", str(wav)], check=True)
            audio_parts.append(wav)
            slide_total = ffprobe_duration(wav)
            speech_dur = slide_total - LEAD - TAIL
            cues = caption_times(text, bounds, speech_dur)
            cursor = 0.0
            for cs, ce, cap in cues:
                cs, ce = max(cs, cursor), min(ce, speech_dur)
                if ce <= cs:
                    continue
                add_frame(png, None, LEAD + cs - cursor if cursor == 0.0 else cs - cursor)
                add_frame(png, cap, ce - cs)
                k += 1
                srt.append(f"{k}\n{srt_time(t + LEAD + cs)} --> {srt_time(t + LEAD + ce)}\n{cap}\n")
                cursor = ce
            add_frame(png, None, slide_total - LEAD - cursor)
            t += slide_total
        script.append(f"## Slide {i} ({srt_time(start_t)[:8]} to {srt_time(t)[:8]})\n\n{sl['narration']}\n")

    lst = tmp / "frames.txt"
    lines = []
    for f, d in frames:
        lines += [f"file '{f}'", f"duration {d:.3f}"]
    lines.append(f"file '{frames[-1][0]}'")
    lst.write_text("\n".join(lines) + "\n")
    mp4 = out_dir / f"{a.name}.mp4"
    if a.no_tts:
        audio_in = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    else:
        alist = tmp / "audio.txt"
        alist.write_text("".join(f"file '{p}'\n" for p in audio_parts))
        full_wav = tmp / "audio.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(alist), "-c", "copy", str(full_wav)], check=True)
        audio_in = ["-i", str(full_wav)]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), *audio_in,
                    "-vf", f"fps={FPS},format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", str(a.crf), "-c:a", "aac", "-b:a", "96k", "-shortest",
                    "-movflags", "+faststart", str(mp4)], check=True)
    (out_dir / f"{a.name}.srt").write_text("\n".join(srt))
    (out_dir / f"{a.name}_narration_script.md").write_text("\n".join(script))
    shutil.rmtree(tmp, ignore_errors=True)
    dur = ffprobe_duration(mp4)
    print(f"wrote {mp4} ({mp4.stat().st_size / 1e6:.1f} MB, {dur / 60:.1f} min, {k} captions, voice={'none' if a.no_tts else a.voice})")


if __name__ == "__main__":
    main()
