#!/usr/bin/env python3
"""Drive the official Even Hub simulator, record GlancePx, mux a narrated demo."""

from __future__ import annotations

import json
import struct
import subprocess
import time
import urllib.request
import zlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/workspace/competitions-2/even-glancepx")
OUT_MP4 = ROOT / "demo.mp4"
OUT_SRT = ROOT / "demo.srt"
LOGO = ROOT / "logo.png"
COVER = ROOT / "cover.png"
WORK = Path("/tmp/glancepx-demo")
SHOTS = WORK / "shots"
AUDIO = WORK / "audio"
FRAMES = WORK / "frames"
AUTOMATION = "http://127.0.0.1:9898"
EDGE_TTS = "/workspace/codegeist/.venv-video/bin/edge-tts"
VOICE = "en-US-AndrewNeural"
W, H = 1920, 1080
SCALE = 2  # placeholder, see DISPLAY_SIZE
CANVAS_W, CANVAS_H = 1440, 720  # 2.5×, leaves ~260px for captions
BG = (5, 8, 5)
GREEN = (80, 255, 80)
DIM = (40, 110, 40)
WHITE = (230, 240, 230)

NARRATION = [
    # key, on-screen beat, spoken text
    ("title", "title", "GlancePx is a glance-and-act market ticker for Even Realities G2 glasses."),
    (
        "quotes",
        "quotes",
        "It is running in the official Even Hub simulator, on the five seventy-six by two eighty-eight monochrome display. Live U.S. dollar quotes for Bitcoin, Ethereum, Solana, and BNB, from CoinGecko.",
    ),
    (
        "swipe",
        "eth",
        "Swipe the temple to move the focus. One glance, four coins, no phone.",
    ),
    (
        "sol",
        "sol",
        "Solana, then BNB. The focused row is marked, and the confirm action follows it.",
    ),
    (
        "bnb",
        "bnb",
        "When a move matters, go back to Bitcoin, and one tap opens a paper price alert. No typing.",
    ),
    (
        "confirm",
        "confirm",
        "The five percent target is already filled in. This is a paper alert, on the device only. No order is sent, and no funds are held.",
    ),
    (
        "done",
        "done",
        "Tap once to confirm. The alert is stored on the device, and will flag on the next refresh.",
    ),
    (
        "back",
        "quotes_alert",
        "GlancePx. Track two, Crypto and DeFi. Built for the Heads Up hackathon, with no API keys and no custody.",
    ),
]


def http_json(url: str, data: dict | None = None, timeout: float = 5):
    body = None
    headers = {}
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as res:
        raw = res.read()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def wait_ping(seconds: float = 20) -> None:
    deadline = time.time() + seconds
    while time.time() < deadline:
        try:
            if http_json(f"{AUTOMATION}/api/ping") is not None or True:
                # ping returns b'pong'
                with urllib.request.urlopen(f"{AUTOMATION}/api/ping", timeout=1) as res:
                    if res.read() == b"pong":
                        return
        except Exception:
            time.sleep(0.25)
    raise SystemExit("simulator automation port did not come up")


def send_input(action: str) -> None:
    http_json(f"{AUTOMATION}/api/input", {"action": action})
    time.sleep(0.45)


def fetch_glasses(dest: Path) -> Path:
    with urllib.request.urlopen(f"{AUTOMATION}/api/screenshot/glasses", timeout=5) as res:
        dest.write_bytes(res.read())
    return dest


def png_on_black(src: Path, dest: Path) -> Path:
    """Composite the official RGBA screenshot (green + alpha) onto black."""
    im = Image.open(src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
    out = Image.alpha_composite(bg, im).convert("RGB")
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest)
    return dest


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def make_logo() -> None:
    size = 1024
    im = Image.new("RGB", (size, size), (8, 12, 8))
    d = ImageDraw.Draw(im)
    # faint grid
    for x in range(64, size, 64):
        d.line([(x, 80), (x, size - 200)], fill=(16, 32, 16), width=1)
    for y in range(80, size - 200, 64):
        d.line([(64, y), (size - 64, y)], fill=(16, 32, 16), width=1)
    # sparkline
    pts = [(120, 620), (250, 540), (370, 580), (500, 360), (640, 400), (780, 220), (900, 180)]
    d.line(pts, fill=GREEN, width=18, joint="curve")
    # arrow head
    d.polygon([(900, 180), (830, 210), (880, 250)], fill=GREEN)
    d.text((120, 820), "GLANCEPX", fill=GREEN, font=font(92, bold=True))
    d.text((124, 930), "G2  ·  TRACK 02  ·  CRYPTO", fill=DIM, font=font(28))
    im.save(LOGO)
    print("logo", LOGO)


def make_cover(quotes_frame: Path | None = None) -> None:
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 8], fill=GREEN)
    d.text((80, 80), "GLANCEPX", fill=GREEN, font=font(92, bold=True))
    d.text((84, 190), "A glance-and-act market ticker for Even Realities G2", fill=WHITE, font=font(36))
    d.text((84, 250), "Heads Up hackathon  ·  Track 02 Crypto & DeFi  ·  CoinGecko", fill=DIM, font=font(28))
    if quotes_frame and quotes_frame.exists():
        g = Image.open(quotes_frame).convert("RGB")
        g = g.resize((1152, 576), Image.Resampling.NEAREST)
        x, y = (W - 1152) // 2, 360
        d.rectangle([x - 4, y - 4, x + 1152 + 3, y + 576 + 3], outline=GREEN, width=3)
        im.paste(g, (x, y))
    im.save(COVER)
    print("cover", COVER)


def base_frame(label_right: str) -> Image.Image:
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 6], fill=GREEN)
    d.text((48, 18), "GLANCEPX", fill=GREEN, font=font(28, bold=True))
    d.text((240, 24), "Even Hub official simulator   ·   576 × 288 monochrome", fill=DIM, font=font(20))
    # right label
    bbox = d.textbbox((0, 0), label_right, font=font(18))
    d.text((W - 48 - (bbox[2] - bbox[0]), 26), label_right, fill=DIM, font=font(18))
    return im


def paste_glasses(im: Image.Image, glasses_rgb: Path) -> Image.Image:
    g = Image.open(glasses_rgb).convert("RGB")
    g = g.resize((CANVAS_W, CANVAS_H), Image.Resampling.NEAREST)
    x = (W - CANVAS_W) // 2
    y = 72
    d = ImageDraw.Draw(im)
    d.rectangle([x - 6, y - 6, x + CANVAS_W + 5, y + CANVAS_H + 5], outline=GREEN, width=3)
    im.paste(g, (x, y))
    # footer hint above subtitle area
    d.text((x, y + CANVAS_H + 14), "G2 glasses display  ·  paper alerts only, no custody", fill=DIM, font=font(18))
    return im


def title_card() -> Image.Image:
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 8], fill=GREEN)
    d.text((160, 320), "GLANCEPX", fill=GREEN, font=font(140, bold=True))
    d.text((168, 480), "Glance-and-act prices on Even Realities G2", fill=WHITE, font=font(40))
    d.text((168, 560), "Track 02  ·  Crypto & DeFi  ·  CoinGecko", fill=DIM, font=font(32))
    d.text((168, 720), "Official Even Hub simulator demo", fill=DIM, font=font(28))
    d.text((168, 920), "Heads Up hackathon  ·  no API keys  ·  no live orders", fill=DIM, font=font(24))
    return im


def end_card() -> Image.Image:
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 8], fill=GREEN)
    d.text((160, 360), "GLANCEPX", fill=GREEN, font=font(120, bold=True))
    d.text((168, 520), "github.com/w1nter625/glancepx", fill=WHITE, font=font(40))
    d.text((168, 620), "Track 02  ·  Crypto & DeFi", fill=DIM, font=font(32))
    d.text((168, 800), "Built during the Heads Up build window. MIT license.", fill=DIM, font=font(24))
    return im


def capture_sequence() -> dict[str, Path]:
    SHOTS.mkdir(parents=True, exist_ok=True)
    FRAMES.mkdir(parents=True, exist_ok=True)
    wait_ping()
    time.sleep(1.2)  # let the first CoinGecko refresh land

    def snap(name: str) -> Path:
        raw = SHOTS / f"{name}.raw.png"
        black = SHOTS / f"{name}.png"
        fetch_glasses(raw)
        png_on_black(raw, black)
        print("captured", name, black.stat().st_size)
        return black

    # If we are not on quotes (e.g. leftover confirm page), double-click goes back
    # without exiting, because exit is only on the quotes root page.
    # We restart from whatever state by going back twice at most, then rely on
    # a quotes snapshot. Safer: just start after a fresh simulator boot.
    quotes = snap("quotes")
    send_input("down")
    eth = snap("eth")
    send_input("down")
    sol = snap("sol")
    send_input("down")
    bnb = snap("bnb")
    send_input("down")  # wrap to BTC
    time.sleep(0.2)
    snap("btc_again")
    send_input("click")
    confirm = snap("confirm")
    send_input("click")
    done = snap("done")
    send_input("click")
    quotes_alert = snap("quotes_alert")
    return {
        "quotes": quotes,
        "eth": eth,
        "sol": sol,
        "bnb": bnb,
        "confirm": confirm,
        "done": done,
        "quotes_alert": quotes_alert,
    }


def tts(key: str, text: str) -> tuple[Path, Path, float]:
    AUDIO.mkdir(parents=True, exist_ok=True)
    mp3 = AUDIO / f"{key}.mp3"
    srt = AUDIO / f"{key}.srt"
    if mp3.exists() and mp3.stat().st_size >= 1000 and srt.exists():
        dur = float(
            subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
                text=True,
            ).strip()
        )
        print(f"tts {key}: {dur:.2f}s (cached)")
        return mp3, srt, dur
    last_err = None
    for attempt in range(1, 6):
        try:
            if mp3.exists():
                mp3.unlink()
            subprocess.run(
                [
                    EDGE_TTS,
                    "--voice",
                    VOICE,
                    "--rate=-5%",
                    "--text",
                    text,
                    "--write-media",
                    str(mp3),
                    "--write-subtitles",
                    str(srt),
                    "--no-progress",
                ],
                check=True,
            )
            if mp3.exists() and mp3.stat().st_size >= 1000:
                break
            last_err = f"tiny file ({mp3.stat().st_size if mp3.exists() else 0} bytes)"
        except subprocess.CalledProcessError as e:
            last_err = e
        time.sleep(1.5 * attempt)
    else:
        raise SystemExit(f"TTS failed for {key}: {last_err}")
    dur = float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3)],
            text=True,
        ).strip()
    )
    print(f"tts {key}: {dur:.2f}s")
    return mp3, srt, dur


def ts(x: float) -> str:
    if x < 0:
        x = 0
    h = int(x // 3600)
    m = int(x % 3600 // 60)
    s = x % 60
    return f"{h:02}:{m:02}:{int(s):02},{int(round((s - int(s)) * 1000)):03}"


def parse_ts(s: str) -> float:
    h, m, r = s.split(":")
    sec, ms = r.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def render_still(kind: str, glasses: Path | None, dest: Path) -> None:
    if kind == "title":
        im = title_card()
    elif kind == "end":
        im = end_card()
    else:
        labels = {
            "quotes": "LIVE QUOTES",
            "eth": "SWIPE  ·  ETH",
            "sol": "SWIPE  ·  SOL",
            "bnb": "SWIPE  ·  BNB",
            "confirm": "PAPER ALERT",
            "done": "ALERT SET",
            "quotes_alert": "BACK TO QUOTES",
        }
        im = base_frame(labels.get(kind, kind.upper()))
        assert glasses is not None
        paste_glasses(im, glasses)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, optimize=True)


def build_video(shots: dict[str, Path]) -> float:
    FRAMES.mkdir(parents=True, exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)
    # extra end card with a short silence after the last line
    items = list(NARRATION)
    segs = []
    srt_blocks = []
    n = 1
    off = 0.0
    pad_after = 0.7
    pre_roll = 0.25

    for key, beat, text in items:
        mp3, part_srt, dur = tts(key, text)
        hold = dur + pre_roll + pad_after
        frame = FRAMES / f"{key}.png"
        if beat == "title":
            render_still("title", None, frame)
        else:
            render_still(beat, shots[beat], frame)
        out = WORK / f"seg_{key}.mp4"
        fade_out_start = max(0.05, hold - 0.25)
        vf = f"fade=t=in:st=0:d=0.2,fade=t=out:st={fade_out_start:.2f}:d=0.25,format=yuv420p"
        subprocess.run(
            [
                "ffmpeg", "-y", "-loglevel", "error",
                "-loop", "1", "-framerate", "30", "-i", str(frame),
                "-i", str(mp3),
                "-af", f"adelay={int(pre_roll*1000)}|{int(pre_roll*1000)},apad",
                "-t", f"{hold:.2f}",
                "-vf", vf,
                "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
                "-pix_fmt", "yuv420p",
                str(out),
            ],
            check=True,
        )
        segs.append(out)
        raw = part_srt.read_text().strip()
        if raw:
            for blk in raw.split("\n\n"):
                lines = blk.split("\n")
                if len(lines) < 3:
                    continue
                a, b = lines[1].split(" --> ")
                txt = " ".join(lines[2:])
                srt_blocks.append(
                    f"{n}\n{ts(off + pre_roll + parse_ts(a))} --> {ts(off + pre_roll + parse_ts(b))}\n{txt}\n"
                )
                n += 1
        off += hold

    # short end card, no speech
    end_hold = 3.2
    end_frame = FRAMES / "end.png"
    render_still("end", None, end_frame)
    end_out = WORK / "seg_end.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-loop", "1", "-framerate", "30", "-i", str(end_frame),
            "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
            "-t", f"{end_hold:.2f}",
            "-vf", "fade=t=in:st=0:d=0.3,format=yuv420p",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
            "-pix_fmt", "yuv420p", "-shortest",
            str(end_out),
        ],
        check=True,
    )
    segs.append(end_out)
    off += end_hold

    lst = WORK / "list.txt"
    lst.write_text("".join(f"file '{s}'\n" for s in segs))
    OUT_SRT.write_text("\n".join(srt_blocks) + "\n")
    raw = WORK / "raw.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(raw)],
        check=True,
    )
    # burn subtitles
    style = (
        "FontName=DejaVu Sans,FontSize=28,PlayResX=1920,PlayResY=1080,"
        "PrimaryColour=&H00EAFFEA,OutlineColour=&H80000000,BackColour=&H90000000,"
        "BorderStyle=3,Outline=2,Shadow=0,MarginV=36,Alignment=2"
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", str(raw),
            "-vf", f"subtitles={OUT_SRT}:force_style='{style}'",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18",
            "-c:a", "copy",
            "-movflags", "+faststart",
            "-pix_fmt", "yuv420p",
            str(OUT_MP4),
        ],
        check=True,
    )
    print("wrote", OUT_MP4, "duration", round(off, 2))
    return off


def load_existing_shots() -> dict[str, Path]:
    needed = ["quotes", "eth", "sol", "bnb", "confirm", "done", "quotes_alert"]
    out = {}
    for k in needed:
        p = SHOTS / f"{k}.png"
        if not p.exists():
            raise SystemExit(f"missing shot {p}")
        out[k] = p
    return out

def main() -> None:
    import os
    make_logo()
    if os.environ.get("SKIP_CAPTURE") == "1":
        shots = load_existing_shots()
    else:
        shots = capture_sequence()
    make_cover(shots["quotes"])
    total = build_video(shots)
    probe = float(
        subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(OUT_MP4)],
            text=True,
        ).strip()
    )
    print("FINAL", OUT_MP4, f"{probe:.2f}s", OUT_MP4.stat().st_size, "bytes")
    if probe > 180:
        raise SystemExit(f"demo is {probe:.1f}s, over the 3 minute limit")


if __name__ == "__main__":
    main()
