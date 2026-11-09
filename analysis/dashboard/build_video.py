"""Build the captioned overview video from the deck and the narration in deck_data.json.

Inputs: reports/deck/gp_rarelink_overview.pdf (rendered from the deck by LibreOffice) and the per-slide
narration in analysis/dashboard/deck_data.json. Outputs, in reports/video/:
  gp_rarelink_overview.mp4   1280x720, H.264, silent stereo track, captions burnt in
  gp_rarelink_overview.srt   the same captions as subtitles
  narration_script.md        the word-for-word script with timecodes, for a voice-over

No speech synthesis is available in this environment, so the video is captioned and the script is for a
person to record over it (Jimmy's choice, 2026-11-09).

  uv run python -m analysis.dashboard.build_video
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
DECK_PDF = ROOT / "reports/deck/gp_rarelink_overview.pdf"
DATA = ROOT / "analysis/dashboard/deck_data.json"
OUT = ROOT / "reports/video"
W, H = 1280, 720
WORDS_PER_SECOND = 2.5  # 150 words a minute, a comfortable reading pace
LEAD_IN = 0.8           # seconds a slide shows before its first caption
MIN_CAPTION = 2.2
MAX_CHARS = 92          # per caption chunk (two lines)
FONT_CANDIDATES = ["/usr/share/fonts/opentype/inter/Inter-Medium.otf", "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]


def font(size):
    for f in FONT_CANDIDATES:
        if Path(f).exists():
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def chunk(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    """Split narration into caption-sized chunks at sentence, then clause, boundaries."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks: list[str] = []
    for s in sentences:
        if len(s) <= max_chars:
            chunks.append(s)
            continue
        parts = re.split(r"(?<=[;:,])\s+", s)
        cur = ""
        for p in parts:
            if cur and len(cur) + 1 + len(p) > max_chars:
                chunks.append(cur)
                cur = p
            else:
                cur = f"{cur} {p}".strip()
        if cur:
            chunks.append(cur)
    # merge very short tails into the previous chunk
    merged: list[str] = []
    for c in chunks:
        if merged and len(c) < 30 and len(merged[-1]) + 1 + len(c) <= max_chars:
            merged[-1] = f"{merged[-1]} {c}"
        else:
            merged.append(c)
    return merged


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
    im = Image.open(slide_png).convert("RGB").resize((W, H), Image.LANCZOS)
    if caption:
        draw = ImageDraw.Draw(im, "RGBA")
        lines = wrap(draw, caption, fnt, W - 160)
        line_h = 38
        band_h = 36 + line_h * len(lines)
        draw.rectangle([0, H - band_h, W, H], fill=(11, 11, 11, 190))
        y = H - band_h + 18
        for ln in lines:
            tw = draw.textlength(ln, font=fnt)
            draw.text(((W - tw) / 2, y), ln, font=fnt, fill=(255, 255, 255, 255))
            y += line_h
    im.save(out, "PNG", optimize=False)


def srt_time(t: float) -> str:
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def main():
    data = json.loads(DATA.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="gp_video_"))
    subprocess.run(["pdftoppm", "-png", "-scale-to-x", str(W), "-scale-to-y", str(H), str(DECK_PDF), str(tmp / "slide")], check=True)
    slides = sorted(tmp.glob("slide-*.png"))
    if len(slides) != len(data["slides"]):
        raise SystemExit(f"{len(slides)} slide images but {len(data['slides'])} narration entries")
    fnt = font(26)
    concat, srt, script = [], [], [f"# Narration script: GP-RareLink overview video\n", f"*Generated {data['date']} from `analysis/dashboard/deck_data.json`; about 150 words a minute. Read each block while its slide is on screen; the video shows the same text as captions.*\n"]
    t, n, k = 0.0, 0, 0
    for i, (png, sl) in enumerate(zip(slides, data["slides"]), start=1):
        start_t = t
        f = tmp / f"f{n:04d}.png"
        frame(png, None, f, fnt)
        concat.append((f, LEAD_IN))
        t += LEAD_IN
        n += 1
        for c in chunk(sl["narration"]):
            dur = max(MIN_CAPTION, len(c.split()) / WORDS_PER_SECOND + 0.35)
            f = tmp / f"f{n:04d}.png"
            frame(png, c, f, fnt)
            concat.append((f, dur))
            k += 1
            srt.append(f"{k}\n{srt_time(t)} --> {srt_time(t + dur)}\n{c}\n")
            t += dur
            n += 1
        script.append(f"## Slide {i} ({srt_time(start_t)[:8]} to {srt_time(t)[:8]})\n\n{sl['narration']}\n")
    lst = tmp / "list.txt"
    lines = []
    for f, dur in concat:
        lines += [f"file '{f}'", f"duration {dur:.3f}"]
    lines.append(f"file '{concat[-1][0]}'")  # concat demuxer needs the last file repeated
    lst.write_text("\n".join(lines) + "\n")
    mp4 = OUT / "gp_rarelink_overview.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-c:a", "aac", "-b:a", "64k", "-shortest",
                    "-movflags", "+faststart", str(mp4)], check=True)
    (OUT / "gp_rarelink_overview.srt").write_text("\n".join(srt))
    (OUT / "narration_script.md").write_text("\n".join(script))
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"wrote {mp4} ({mp4.stat().st_size / 1e6:.1f} MB, {t / 60:.1f} min, {k} captions), .srt and narration_script.md")


if __name__ == "__main__":
    main()
