"""Shared helpers for the Blue March puppet clips.

Each render_<state>.py builds a mono mix with `Mix`, defines `frame(t) -> PIL.Image`
and calls `render(...)`. Drawing happens at SS x supersampling in a 1280x720 frame.
"""
import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FPS, W, H, SS, SR = 24, 1280, 720, 2, 44100
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CLIPS = os.path.join(ROOT, "public", "clips")
FB = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
FR = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(p, size): return ImageFont.truetype(p, int(size))


# ---------------------------------------------------------------- easing / timing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x
def back(x):
    x = clamp(x); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def keyed(t, keys):
    """keys: [(t, v1, v2, ...)] -> eased interpolation of the values at time t."""
    if t <= keys[0][0]: return keys[0][1:]
    for (t0, *a), (t1, *b) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            x = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1
            return tuple(lerp(p, q, x) for p, q in zip(a, b))
    return keys[-1][1:]


class Mouth:
    """Mouth openness 0..1 from word spans [(start, end)] in video time."""
    def __init__(s, spans): s.spans = [(a, max(0.12, b - a)) for a, b in spans]
    def __call__(s, t):
        for ws, d in s.spans:
            if ws <= t < ws + d:
                x = (t - ws) / d
                return math.sin(math.pi * x) * (0.75 + 0.25 * math.sin(t * 31))
        return 0.0


# ---------------------------------------------------------------- audio
def load(src, a, b):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-to", str(b), "-i", src,
                          "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def fade(sig, fin=0.15, fout=0.3):
    t = np.arange(len(sig)) / SR; L = len(sig) / SR
    return sig * np.clip(t / max(fin, 1e-3), 0, 1) * np.clip((L - t) / max(fout, 1e-3), 0, 1)


class Mix:
    def __init__(s, dur): s.buf = np.zeros(int(dur * SR) + 1, np.float32); s.dur = dur
    def add(s, sig, t0, gain=1.0):
        i = int(t0 * SR); m = min(len(sig), len(s.buf) - i)
        if m > 0: s.buf[i:i + m] += sig[:m] * gain
    def write(s, path):
        b = s.buf * min(1.0, 0.95 / max(1e-6, np.abs(s.buf).max()))
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
            wf.writeframes((b * 32767).astype(np.int16).tobytes())


def sfx_pop(f0=520, d=0.18, g=0.35):
    t = np.arange(int(d * SR)) / SR
    return (np.sin(2 * np.pi * (f0 + 900 * t) * t) * np.exp(-t * 22) * g).astype(np.float32)


def sfx_chime(t_gain=0.22):
    out = []
    for k, f in enumerate([523.25, 659.25, 783.99, 1046.5]):
        d = 0.45 if k == 3 else 0.13
        t2 = np.arange(int(d * SR)) / SR
        out.append(((np.sin(2 * np.pi * f * t2) + 0.3 * np.sin(4 * np.pi * f * t2)) * np.exp(-t2 * (4 if k == 3 else 9)) * t_gain).astype(np.float32))
    return out  # play out[k] at t0 + k*0.11


def sfx_boing(d=0.5, g=0.3):
    t = np.arange(int(d * SR)) / SR
    f = 180 + 120 * np.sin(2 * np.pi * 7 * t) * np.exp(-t * 3)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4) * g).astype(np.float32)


def sfx_snip(g=0.4):
    rng = np.random.default_rng(7); t = np.arange(int(0.07 * SR)) / SR
    return (rng.uniform(-1, 1, len(t)) * np.exp(-t * 90) * g).astype(np.float32)


# ---------------------------------------------------------------- drawing
class D:
    def __init__(s, img): s.d = ImageDraw.Draw(img)
    def e(s, cx, cy, rx, ry, fill, outline=None, w=0):
        s.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=fill, outline=outline, width=int(w * SS))
    def r(s, x0, y0, x1, y1, fill, rad=0, outline=None, w=0):
        s.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=rad * SS, fill=fill, outline=outline, width=int(w * SS))
    def p(s, pts, fill, outline=None, w=0):
        s.d.polygon([(x * SS, y * SS) for x, y in pts], fill=fill, outline=outline, width=int(w * SS))
    def l(s, pts, fill, w):
        s.d.line([(x * SS, y * SS) for x, y in pts], fill=fill, width=max(1, int(w * SS)), joint="curve")
        for x, y in (pts[0], pts[-1]): s.e(x, y, w / 2, w / 2, fill)
    def a(s, cx, cy, rx, ry, a0, a1, fill, w):
        s.d.arc([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], a0, a1, fill=fill, width=max(1, int(w * SS)))
    def chord(s, cx, cy, rx, ry, a0, a1, fill, outline=None, w=0):
        s.d.chord([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], a0, a1, fill=fill, outline=outline, width=int(w * SS))
    def pie(s, cx, cy, rx, ry, a0, a1, fill, outline=None, w=0):
        s.d.pieslice([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], a0, a1, fill=fill, outline=outline, width=int(w * SS))
    def text(s, x, y, txt, size, fill, anchor="mm", stroke=0, sf=None, bold=True):
        s.d.text((x * SS, y * SS), txt, font=font(FB if bold else FR, size * SS), fill=fill, anchor=anchor,
                 stroke_width=int(stroke * SS), stroke_fill=sf)
    def star(s, cx, cy, R, fill):
        pts = []
        for k in range(10):
            rr = R if k % 2 == 0 else R * 0.42
            ang = math.radians(-90 + k * 36)
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        s.p(pts, fill)
    def heart(s, cx, cy, r, fill):
        s.e(cx - r * 0.5, cy - r * 0.3, r * 0.55, r * 0.55, fill); s.e(cx + r * 0.5, cy - r * 0.3, r * 0.55, r * 0.55, fill)
        s.p([(cx - r * 1.02, cy - r * 0.15), (cx + r * 1.02, cy - r * 0.15), (cx, cy + r)], fill)


def gradient(c0, c1):
    g = np.linspace(0, 1, H * SS)[:, None, None]
    arr = (np.array(c0) * (1 - g) + np.array(c1) * g).astype(np.uint8)
    return Image.fromarray(np.repeat(arr, W * SS, axis=1), "RGB")


def glow(img, spots, blur=60):
    """spots: [(cx, cy, rx, ry, rgba)] soft light blobs."""
    g = Image.new("RGBA", img.size, (0, 0, 0, 0)); gd = D(g)
    for cx, cy, rx, ry, c in spots: gd.e(cx, cy, rx, ry, c)
    g = g.filter(ImageFilter.GaussianBlur(blur * SS))
    return Image.alpha_composite(img.convert("RGBA"), g).convert("RGB")


def shade(c, k): return tuple(max(0, min(255, int(v * k))) for v in c)


# Generic puppet head: big felt head, googly-ish eyes, hinge mouth (Muppet/latex hybrid).
def puppet_head(d, hx, hy, s, skin, mo=0.0, brow=0.0, look=(0, 0), blink=False, blush=0.0,
                rx=88, ry=100, nose=None, ear=True, eye_gap=34, beard=None, teeth=False):
    sd = shade(skin, 0.8)
    if ear:
        for sx in (-1, 1): d.e(hx + sx * (rx - 2) * s, hy + 5 * s, 15 * s, 24 * s, skin, sd, 3 * s)
    d.e(hx, hy, rx * s, ry * s, skin, sd, 4 * s)
    if blush > 0:
        for sx in (-1, 1): d.e(hx + sx * 52 * s, hy + 26 * s, 22 * s, 13 * s, lerp_c(skin, (236, 110, 125), blush))
    for sx in (-1, 1):
        ex, ey = hx + sx * eye_gap * s, hy - 14 * s
        if blink:
            d.a(ex, ey, 14 * s, 8 * s, 20, 160, (40, 25, 20), 4 * s)
        else:
            d.e(ex, ey, 15 * s, 13 * s, (255, 255, 255), (60, 40, 30), 2 * s)
            d.e(ex + look[0] * 5 * s, ey + look[1] * 4 * s, 6 * s, 6 * s, (25, 25, 30))
    if beard:
        d.chord(hx, hy + 4 * s, (rx - 1) * s, (ry - 4) * s, 8, 172, beard)
        d.e(hx, hy + 44 * s, 30 * s, 14 * s, beard)
    d.e(hx, hy + 14 * s, 12 * s, 16 * s, nose or shade(skin, 0.9))
    my = hy + 52 * s
    if teeth and mo < 0.08:
        d.chord(hx, my - 10 * s, 30 * s, 20 * s, 0, 180, (250, 248, 235), (120, 50, 45), 3 * s)
        for k in (-14, -5, 5, 14): d.l([(hx + k * s, my - 9 * s), (hx + k * s, my + 6 * s)], (200, 195, 185), 1.5 * s)
    elif mo < 0.08:
        d.a(hx, my - 8 * s, 24 * s, 12 * s, 20, 160, (110, 40, 40), 5 * s)
    else:
        ry2 = (6 + 24 * mo) * s
        d.e(hx, my, (22 + 6 * mo) * s, ry2, (90, 20, 30), (120, 50, 45), 4 * s)
        d.r(hx - 14 * s, my - ry2 + 3 * s, hx + 14 * s, my - ry2 + 9 * s, (250, 248, 235), 3 * s)
    return hy - 14 * s - (24 + 10 * brow) * s  # brow y, for callers drawing brows


def lerp_c(a, b, x): return tuple(int(lerp(p, q, clamp(x))) for p, q in zip(a, b))


def suit(d, hx, by, s, cloth, shirt=(245, 245, 245), tie=(200, 35, 45), neck=None):
    if neck: d.r(hx - 24 * s, by - 26 * s, hx + 24 * s, by + 10, neck)
    d.p([(hx - 118 * s, by), (hx + 118 * s, by), (hx + 150 * s, by + 330), (hx - 150 * s, by + 330)], cloth)
    d.p([(hx - 38 * s, by), (hx + 38 * s, by), (hx, by + 88 * s)], shirt)
    if tie:
        d.p([(hx - 13 * s, by + 10 * s), (hx + 13 * s, by + 10 * s), (hx + 21 * s, by + 250 * s), (hx, by + 280 * s), (hx - 21 * s, by + 250 * s)], tie)
        d.e(hx, by + 14 * s, 14 * s, 10 * s, shade(tie, 0.85))


def hand(d, x, y, s, skin):
    sd = shade(skin, 0.8)
    for k in range(4): d.e(x - 24 * s + k * 16 * s, y - 30 * s, 9 * s, 16 * s, skin, sd, 2 * s)
    d.e(x + 32 * s, y - 2 * s, 10 * s, 16 * s, skin, sd, 2 * s)
    d.e(x, y, 34 * s, 30 * s, skin, sd, 3 * s)


def caption(od, t, caps, fnt):
    for a, b, txt in caps:
        if a <= t < b:
            tw = od.textlength(txt, font=fnt)
            od.rounded_rectangle([640 - tw / 2 - 22, 628, 640 + tw / 2 + 22, 682], 12, fill=(0, 0, 0, 170))
            od.text((640, 655), txt, font=fnt, fill=(255, 255, 255), anchor="mm")


def compose(img, z, cx, cy, t, caps):
    cw, ch = W * SS / z, H * SS / z
    x0 = min(max(cx * SS - cw / 2, 0), W * SS - cw); y0 = min(max(cy * SS - ch / 2, 0), H * SS - ch)
    out = img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    caption(od, t, caps, font(FR, 30))
    return Image.alpha_composite(out, ov).convert("RGB")


def render(name, frame, dur, wav, stills_at):
    """`python render_x.py --stills` writes a contact sheet; otherwise writes public/clips/<name>.mp4."""
    tmp = os.path.join(os.path.dirname(wav))
    if "--stills" in sys.argv:
        ims = [frame(t).resize((W // 2, H // 2)) for t in stills_at]
        cols = 3; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (W // 2 * cols, H // 2 * rows))
        for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * W // 2, (i // cols) * H // 2))
        p = os.path.join(tmp, f"{name}_stills.png"); sheet.save(p); print("stills", p); return
    out = os.path.join(CLIPS, f"{name}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-preset", "medium",
                           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    print("video", out)


# ---------------------------------------------------------------- Trump (same puppet as the Texas clip)
SK, SKD = (242, 166, 90), (196, 120, 55)
HAIR, HAIRD = (247, 208, 74), (214, 168, 40)
SUIT = (32, 42, 74)

def trump_head(d, hx, hy, s, mo=0.0, wink=False):
    d.e(hx - 88 * s, hy + 5 * s, 16 * s, 26 * s, SK, SKD, 3 * s)
    d.e(hx + 88 * s, hy + 5 * s, 16 * s, 26 * s, SK, SKD, 3 * s)
    d.e(hx, hy, 90 * s, 100 * s, SK, SKD, 4 * s)
    for sx in (-1, 1):
        d.e(hx + sx * 36 * s, hy - 12 * s, 27 * s, 18 * s, (250, 222, 180))
    d.e(hx - 36 * s, hy - 12 * s, 13 * s, 9 * s, (255, 255, 255)); d.e(hx - 35 * s, hy - 11 * s, 5 * s, 5 * s, (30, 30, 30))
    if wink:
        d.a(hx + 36 * s, hy - 16 * s, 14 * s, 9 * s, 20, 160, (70, 35, 20), 4 * s)
    else:
        d.e(hx + 36 * s, hy - 12 * s, 13 * s, 9 * s, (255, 255, 255)); d.e(hx + 37 * s, hy - 11 * s, 5 * s, 5 * s, (30, 30, 30))
    d.l([(hx - 58 * s, hy - 36 * s), (hx - 18 * s, hy - 30 * s)], HAIRD, 7 * s)
    d.l([(hx + 18 * s, hy - 30 * s), (hx + 58 * s, hy - (36 + (8 if wink else 0)) * s)], HAIRD, 7 * s)
    d.e(hx, hy + 14 * s, 11 * s, 15 * s, (230, 148, 78))
    my = hy + 54 * s
    if mo < 0.08:
        d.e(hx, my, 21 * s, 10 * s, (170, 70, 60)); d.e(hx, my, 9 * s, 4 * s, (90, 20, 30))
    else:
        ry = (7 + 26 * mo) * s
        d.e(hx, my, (23 + 6 * mo) * s, ry, (90, 20, 30), (170, 70, 60), 4 * s)
        d.r(hx - 15 * s, my - ry + 3 * s, hx + 15 * s, my - ry + 10 * s, (250, 248, 235), 3 * s)
    d.chord(hx, hy - 58 * s, 98 * s, 70 * s, 180, 360, HAIR, HAIRD, 3 * s)
    d.p([(hx - 96 * s, hy - 62 * s), (hx - 132 * s, hy - 34 * s), (hx - 72 * s, hy - 50 * s)], HAIR, HAIRD, 3 * s)
    d.p([(hx + 92 * s, hy - 64 * s), (hx + 104 * s, hy - 24 * s), (hx + 80 * s, hy - 52 * s)], HAIR, HAIRD, 3 * s)
    for k in range(4):
        x0 = hx - 70 * s + k * 38 * s
        d.a(x0 + 30 * s, hy - 84 * s, 40 * s, 22 * s, 190, 330, HAIRD, 3 * s)

def big_hand(d, x, y, s=1.0):
    for k in range(4):
        d.e(x - 27 * s + k * 18 * s, y - 34 * s, 10 * s, 18 * s, SK, SKD, 3 * s)
    d.e(x + 36 * s, y - 2 * s, 11 * s, 18 * s, SK, SKD, 3 * s)
    d.e(x, y, 38 * s, 34 * s, SK, SKD, 3 * s)

