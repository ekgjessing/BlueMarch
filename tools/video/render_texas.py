import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = "/Users/eirik/Downloads/_Pretend that I'm on the ballot._ [kg4neE2V75s].mp3"
WORDS = "/Users/eirik/Documents/GitHub/BlueMarch/lyd/texas-pretend-ballot-ord.tsv"
OUTDIR = "/Users/eirik/Documents/GitHub/BlueMarch/video"
OUT = os.path.join(OUTDIR, "texas-utkast.mp4")
TMP = os.path.dirname(os.path.abspath(__file__))
FPS, DUR, W, H, SS, SR = 24, 15.0, 1280, 720, 2, 44100
OFF = 13.76  # video_t = source_t - OFF  ("So" at 15.76 -> 2.0 s)
os.makedirs(OUTDIR, exist_ok=True)

# ---------------------------------------------------------------- audio
raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "14.0", "-to", "24.7", "-i", SRC,
                      "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
sp = np.frombuffer(raw, np.float32).copy()
tt = np.arange(len(sp)) / SR
sp *= np.clip(tt / 0.5, 0, 1) * np.clip((10.7 - tt) / 0.8, 0, 1)
mix = np.zeros(int(DUR * SR) + 1, np.float32)

def add(sig, t0):
    i = int(t0 * SR); m = min(len(sig), len(mix) - i); mix[i:i + m] += sig[:m]

add(sp, 0.24)
rng = np.random.default_rng(1)
cl = np.arange(int(0.12 * SR)) / SR
add((rng.uniform(-1, 1, len(cl)) * np.exp(-cl * 70) * 0.5).astype(np.float32), 11.55)
add((np.sin(2 * np.pi * 90 * cl) * np.exp(-cl * 30) * 0.5).astype(np.float32), 11.55)
for k, f in enumerate([523.25, 659.25, 783.99, 1046.5]):
    d = 0.45 if k == 3 else 0.13
    t2 = np.arange(int(d * SR)) / SR
    tone = (np.sin(2 * np.pi * f * t2) + 0.3 * np.sin(4 * np.pi * f * t2)) * np.exp(-t2 * (4 if k == 3 else 9)) * 0.22
    add(tone.astype(np.float32), 13.05 + k * 0.11)
mix *= min(1.0, 0.95 / max(1e-6, np.abs(mix).max()))
wav = os.path.join(TMP, "texas_audio.wav")
with wave.open(wav, "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((mix * 32767).astype(np.int16).tobytes())

# ---------------------------------------------------------------- timing
words = []
for line in open(WORDS).read().splitlines()[1:]:
    s, w = line.split("\t")
    if "[" in w: continue
    words.append(float(s) - OFF)
words = [t for t in words if 1.5 < t < 9.5]
spans = []
for i, t in enumerate(words):
    nxt = words[i + 1] if i + 1 < len(words) else t + 0.4
    spans.append((t, max(0.12, min(0.4, nxt - t))))

def mouth(t):
    for ws, d in spans:
        if ws <= t < ws + d: return math.sin(math.pi * (t - ws) / d)
    return 0.0

CAPS = [(2.0, 6.1, "So, I'm asking you to pretend that I'm on the ballot."),
        (6.25, 7.9, "I'm on the ballot."), (7.95, 9.3, "I'm on the ballot.")]

def ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x
def back(x):
    x = max(0.0, min(1.0, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def keyed(t, keys):
    if t <= keys[0][0]: return keys[0][1:]
    for (t0, *a), (t1, *b) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            x = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1
            return tuple(lerp(p, q, x) for p, q in zip(a, b))
    return keys[-1][1:]

# ---------------------------------------------------------------- drawing
FB = "/System/Library/Fonts/Supplemental/Arial Black.ttf"
FR = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
def font(p, size): return ImageFont.truetype(p, int(size))

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
    def text(s, x, y, txt, fnt, fill, anchor="mm", stroke=0, sf=None):
        s.d.text((x * SS, y * SS), txt, font=fnt, fill=fill, anchor=anchor, stroke_width=int(stroke * SS), stroke_fill=sf)
    def star(s, cx, cy, R, fill):
        pts = []
        for k in range(10):
            rr = R if k % 2 == 0 else R * 0.42
            ang = math.radians(-90 + k * 36)
            pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
        s.p(pts, fill)

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

def trump_pose(t):
    def P(mode):
        hx, hy, s = keyed(t, HEAD)
        by = hy + 95 * s
        if mode == "wave":
            w = math.sin(t * 9) * 12
            return [(hx - 200, hy - 40 + w), (hx + 200, hy - 40 - w), (hx - 175, by + 80), (hx + 175, by + 80)]
        if mode == "secret":
            return [(hx - 112 * s, hy + 50 * s), (hx + 120, 452), (hx - 205, by + 110), (hx + 175, by + 110)]
        if mode == "point":
            b = -8 * mouth(t)
            return [(hx - 50, by + 70 + b), (hx + 50, by + 70 + b), (hx - 175, by + 130), (hx + 175, by + 130)]
        return [(492, 470), (788, 470), (420, 400), (860, 400)]
    modes = [(0, "wave"), (2.0, "secret"), (6.15, "point"), (7.95, "lean")]
    i = max(k for k, (t0, _) in enumerate(modes) if t0 <= t)
    cur = P(modes[i][1])
    if i > 0 and t - modes[i][0] < 0.3:
        prv = P(modes[i - 1][1]); x = ease((t - modes[i][0]) / 0.3)
        cur = [(lerp(a[0], b[0], x), lerp(a[1], b[1], x)) for a, b in zip(prv, cur)]
    return cur

HEAD = [(0, 640, 250, 1.0), (2.0, 640, 250, 1.0), (5.0, 640, 262, 1.1), (7.95, 640, 262, 1.1),
        (8.5, 640, 380, 1.35), (9.4, 640, 380, 1.35)]
CAM = [(0, 1.0), (2.0, 1.0), (6.0, 1.10), (7.95, 1.10), (8.15, 1.24), (9.4, 1.26)]

# static backgrounds (hi-res)
def gradient(c0, c1):
    g = np.linspace(0, 1, H * SS)[:, None, None]
    arr = (np.array(c0) * (1 - g) + np.array(c1) * g).astype(np.uint8)
    return Image.fromarray(np.repeat(arr, W * SS, axis=1), "RGB")

bgA = gradient((14, 18, 42), (40, 28, 58))
d = D(bgA)
d.r(190, 30, 1090, 380, (0, 40, 104)); d.r(490, 30, 1090, 205, (236, 236, 236)); d.r(490, 205, 1090, 380, (191, 10, 48))
d.star(340, 205, 92, (245, 245, 245))
dark = Image.new("RGB", bgA.size, (0, 0, 0))
bgA = Image.blend(bgA, dark, 0.35)
glow = Image.new("RGBA", bgA.size, (0, 0, 0, 0)); gd = D(glow)
gd.e(640, 330, 330, 260, (255, 236, 190, 70))
for x in (150, 1130): gd.e(x, 40, 120, 60, (255, 240, 200, 90))
glow = glow.filter(ImageFilter.GaussianBlur(60 * SS))
bgA = Image.alpha_composite(bgA.convert("RGBA"), glow).convert("RGB")

bgB = gradient((70, 44, 56), (28, 24, 42))
bok = Image.new("RGBA", bgB.size, (0, 0, 0, 0)); bd = D(bok)
r = np.random.default_rng(3)
for _ in range(26):
    bd.e(r.uniform(0, W), r.uniform(0, H * 0.7), r.uniform(30, 90), r.uniform(30, 90),
         tuple(int(v) for v in r.choice([(255, 210, 150), (200, 120, 160), (140, 160, 230)])) + (60,))
bok = bok.filter(ImageFilter.GaussianBlur(18 * SS))
bgB = Image.alpha_composite(bgB.convert("RGBA"), bok).convert("RGB")

bgC = gradient((22, 52, 140), (8, 14, 48))
conf = [(r.uniform(0, W), r.uniform(-400, -20), r.uniform(220, 420), r.uniform(0, 6.28),
         tuple(int(v) for v in r.choice([(255, 255, 255), (120, 180, 255), (255, 210, 80), (90, 140, 255)]))) for _ in range(90)]

CROWD = [(60 + k * 116 + (k % 3) * 9, 700 + (k % 2) * 14, k) for k in range(11)]
HATC = [(150, 100, 60), (205, 165, 105), (245, 240, 230), (60, 45, 35), (175, 120, 70)]
HAIRC = [(70, 50, 35), (150, 110, 70), (220, 200, 160), (40, 30, 25), (190, 190, 195)]

def crowd(d, t):
    cheer = 1.0 if (t < 2.0 or t > 9.15) else 0.12
    for x, y, k in CROWD:
        yy = y - cheer * abs(math.sin(t * 8 + k * 1.3)) * 16
        if cheer > 0.5 and k % 2 == 0:
            sx = -1 if k % 4 == 0 else 1
            d.l([(x + sx * 30, yy + 20), (x + sx * 60, yy - 110)], (90, 60, 50), 22)
            d.e(x + sx * 60, yy - 118, 17, 17, (222, 170, 130))
        d.e(x, yy, 50, 58, HAIRC[k % 5])
        hc = HATC[k % 5]
        d.r(x - 40, yy - 98, x + 40, yy - 34, hc, 16)
        d.e(x, yy - 34, 74, 15, hc)
        d.r(x - 40, yy - 52, x + 40, yy - 42, tuple(max(0, c - 50) for c in hc))

def podium(d):
    d.p([(515, 470), (765, 470), (745, 720), (535, 720)], (92, 58, 40), (60, 38, 26), 3)
    d.r(498, 456, 782, 480, (122, 80, 54), 6)
    d.e(640, 585, 50, 50, (30, 70, 160), (240, 240, 240), 4)
    d.star(640, 588, 32, (245, 245, 245))

def scene_a(t):
    img = bgA.copy(); d = D(img)
    hx, hy, s = keyed(t, HEAD)
    lean = ease((t - 7.95) / 0.5)
    mo = mouth(t)
    hy_b = hy - (6 * mo if 6.15 <= t < 7.95 else 0)
    by = hy_b + 95 * s
    lh, rh, le, re = trump_pose(t)
    d.r(hx - 26 * s, hy_b + 70 * s, hx + 26 * s, by + 10, SK)
    d.p([(hx - 120 * s, by), (hx + 120 * s, by), (hx + 150 * s, by + 320), (hx - 150 * s, by + 320)], SUIT)
    d.p([(hx - 40 * s, by), (hx + 40 * s, by), (hx, by + 90 * s)], (245, 245, 245))
    d.p([(hx - 14 * s, by + 10 * s), (hx + 14 * s, by + 10 * s), (hx + 22 * s, by + 270 * s), (hx, by + 300 * s), (hx - 22 * s, by + 270 * s)], (210, 35, 42))
    d.e(hx, by + 14 * s, 15 * s, 11 * s, (180, 25, 32))
    if lean < 0.5:
        for (h, e, sx) in ((lh, le, -1), (rh, re, 1)):
            d.l([(hx + sx * 112 * s, by + 30), e, h], SUIT, 48)
        trump_head(d, hx, hy_b, s, mo, 5.0 <= t < 5.7)
        for h in (lh, rh): big_hand(d, *h, 1.25)
    for x in (622, 658):
        d.l([(x, 458), (x + (x - 640) * 0.4, 405)], (40, 40, 40), 5); d.e(x + (x - 640) * 0.4, 400, 9, 12, (25, 25, 25))
    podium(d)
    if lean >= 0.5:
        for (h, e, sx) in ((lh, le, -1), (rh, re, 1)):
            d.l([(hx + sx * 112 * s, by - 60), e, h], SUIT, 52)
        for h in (lh, rh): big_hand(d, *h, 1.35)
        trump_head(d, hx, hy_b, s, mo, False)
    crowd(d, t)
    return img, keyed(t, CAM)[0], 640, 330

def lady(d, t, hx, hy, smile):
    for ang in list(range(150, 400, 15)):
        a = math.radians(ang); d.e(hx + 122 * math.cos(a), hy - 12 + 136 * math.sin(a), 30, 30, (205, 205, 212), (160, 160, 172), 3)
    d.p([(hx - 150, hy + 120), (hx + 150, hy + 120), (hx + 200, 720), (hx - 200, 720)], (176, 92, 146))
    d.p([(hx - 40, hy + 120), (hx + 40, hy + 120), (hx, hy + 200)], (245, 240, 235))
    d.e(hx, hy, 110, 125, (236, 188, 150), (200, 150, 115), 4)
    for sx in (-1, 1):
        d.e(hx + sx * 62, hy + 40, 20, 12, (240, 160, 150))
        d.e(hx + sx * 40, hy - 8, 8, 8, (40, 30, 30))
        d.e(hx + sx * 40, hy - 8, 30, 30, None, (70, 45, 45), 5)
        d.l([(hx + sx * 62, hy - 46), (hx + sx * 20, hy - 46)], (150, 150, 160), 6)
    d.l([(hx - 10, hy - 8), (hx + 10, hy - 8)], (70, 45, 45), 5)
    d.e(hx, hy + 18, 10, 13, (225, 165, 125))
    if smile: d.a(hx, hy + 50, 26, 16, 20, 160, (150, 60, 70), 5)
    else: d.l([(hx - 22, hy + 62), (hx + 22, hy + 62)], (150, 60, 70), 5)
    hc = (232, 120, 172)
    d.r(hx - 92, hy - 210, hx + 92, hy - 108, hc, 34)
    d.r(hx - 92, hy - 136, hx + 92, hy - 116, (170, 60, 120))
    d.e(hx, hy - 108, 196, 34, hc, (200, 90, 145), 3)

def neighbour(d, hx, hy):
    d.p([(hx - 130, hy + 115), (hx + 130, hy + 115), (hx + 170, 720), (hx - 170, 720)], (178, 52, 48))
    for k in range(-2, 3): d.l([(hx + k * 50, hy + 120), (hx + k * 60, 720)], (130, 30, 30), 8)
    d.e(hx, hy, 95, 110, (222, 170, 130), (180, 130, 95), 4)
    for sx in (-1, 1):
        d.e(hx + sx * 34, hy - 10, 8, 9, (35, 25, 20))
        d.l([(hx + sx * 54, hy - 38), (hx + sx * 16, hy - 34)], (90, 60, 40), 7)
    d.e(hx, hy + 18, 12, 15, (205, 145, 105))
    d.p([(hx - 50, hy + 50), (hx, hy + 38), (hx + 50, hy + 50), (hx + 30, hy + 60), (hx, hy + 52), (hx - 30, hy + 60)], (100, 66, 40))
    d.a(hx, hy + 60, 22, 12, 20, 160, (120, 50, 50), 5)
    hc = (205, 165, 105)
    d.r(hx - 80, hy - 190, hx + 80, hy - 95, hc, 30)
    d.r(hx - 80, hy - 120, hx + 80, hy - 104, (120, 85, 50))
    d.e(hx, hy - 96, 170, 30, hc, (170, 130, 80), 3)

def scene_b(t):
    img = bgB.copy(); d = D(img)
    nod = 0
    if 9.4 <= t < 10.15: nod = 12 * abs(math.sin((t - 9.4) / 0.75 * 2 * math.pi))
    if 12.0 <= t < 13.0: nod = 10 * abs(math.sin((t - 12.0) * 2 * math.pi))
    hx, hy = 540, 290 + nod
    nx = lerp(1460, 1090, ease((t - 11.8) / 0.45))
    nnod = 10 * abs(math.sin((t - 12.3) * 2.2 * math.pi)) if t > 12.3 else 0
    neighbour(d, nx, 360 + nnod)
    lady(d, t, hx, hy, t > 12.2)
    rh = keyed(t, [(9.4, 760, 560), (10.0, 760, 560), (10.4, 1120, 330), (10.55, 1120, 330), (11.45, 610, 592), (11.6, 610, 592), (12.1, 760, 560)])
    cut_s = 0.3
    for sx, h in ((-1, (370, 560)), (1, rh)):
        d.l([(hx + sx * 130, hy + 160), (hx + sx * 175, 620) if sx < 0 else (h[0] - 60, h[1] + 60), h], (176, 92, 146), 46)
    d.r(400, 430, 760, 705, (250, 250, 244), 6, (170, 170, 170), 3)
    d.text(580, 460, "BALLOT", font(FB, 30 * SS), (40, 40, 60))
    for y in (548, 610, 664):
        d.e(440, y, 14, 14, None, (90, 90, 90), 3); d.r(470, y - 6, 720, y + 6, (190, 190, 190), 4)
    for h in ((370, 560), rh):
        d.e(h[0], h[1], 30, 28, (236, 188, 150), (200, 150, 115), 3)
    if t >= 11.55:
        cx, cy = 600, 552
    elif t >= 10.45:
        cx, cy = rh[0] - 10, rh[1] - 40
    else:
        cx = None
    if cx is not None:
        squash = 1.0 + (0.18 * (1 - (t - 11.55) / 0.2) if 11.55 <= t < 11.75 else 0)
        d.e(cx, cy - 10, 108 * cut_s * squash, 148 * cut_s, (255, 255, 255), (200, 200, 200), 2)
        trump_head(d, cx, cy, cut_s)
    if 11.55 <= t < 11.95:
        for k in range(8):
            a = math.radians(k * 45 + 20)
            d.l([(600 + 70 * math.cos(a), 552 + 60 * math.sin(a)), (600 + 105 * math.cos(a), 552 + 90 * math.sin(a))], (255, 240, 120), 6)
        d.text(790, 470, "*click*", font(FB, 40 * SS), (255, 225, 60), stroke=4, sf=(30, 20, 20))
    return img, 1.0, 640, 360

def scene_c(t):
    img = bgC.copy(); d = D(img)
    lt = t - 13.0
    for x, y0, v, ph, c in conf:
        y = y0 + v * lt
        if 0 < y < H: d.r(x + 10 * math.sin(lt * 4 + ph), y, x + 10 * math.sin(lt * 4 + ph) + 10, y + 6, c, 2)
    card = Image.new("RGBA", (580 * SS, 420 * SS), (0, 0, 0, 0)); cd = D(card)
    cd.r(4, 4, 576, 416, (30, 92, 215), 32, (255, 255, 255), 6)
    cd.text(290, 46, "BLUE MARCH", font(FB, 24 * SS), (190, 215, 255))
    cd.star(290, 120, 46, (255, 255, 255))
    cd.text(290, 214, "TEXAS", font(FB, 76 * SS), (255, 255, 255))
    cd.text(290, 274, "UNLOCKED", font(FR, 30 * SS), (220, 235, 255))
    prog = lerp(6, 7, ease((lt - 0.6) / 0.4)) / 48
    cd.r(70, 316, 510, 340, (14, 40, 110), 12)
    cd.r(70, 316, 70 + max(24, 440 * prog), 340, (255, 255, 255), 12)
    cd.text(290, 378, f"{6 if lt < 0.8 else 7} / 48 clips", font(FR, 26 * SS), (255, 255, 255))
    k = back(lt / 0.45)
    if k <= 0.01: return img, 1.0, 640, 360
    cw, ch = int(card.width * k), int(card.height * k)
    card = card.resize((max(1, cw), max(1, ch)), Image.LANCZOS)
    img.paste(card, (int(640 * SS - cw / 2), int(370 * SS - ch / 2)), card)
    return img, 1.0, 640, 360

FCAP = font(FR, 30); FWM = font(FR, 17)

def frame(t):
    if t < 9.4: img, z, cx, cy = scene_a(t)
    elif t < 13.0: img, z, cx, cy = scene_b(t)
    else: img, z, cx, cy = scene_c(t)
    cw, ch = W * SS / z, H * SS / z
    x0 = min(max(cx * SS - cw / 2, 0), W * SS - cw); y0 = min(max(cy * SS - ch / 2, 0), H * SS - ch)
    out = img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.text((18, 14), "DRAFT · animatic", font=FWM, fill=(255, 255, 255, 150))
    for a, b, txt in CAPS:
        if a <= t < b:
            tw = od.textlength(txt, font=FCAP)
            od.rounded_rectangle([640 - tw / 2 - 22, 628, 640 + tw / 2 + 22, 682], 12, fill=(0, 0, 0, 170))
            od.text((640, 655), txt, font=FCAP, fill=(255, 255, 255), anchor="mm")
    return Image.alpha_composite(out, ov).convert("RGB")

if __name__ == "__main__":
    if "--stills" in sys.argv:
        ts = [1.0, 4.4, 5.3, 6.6, 8.8, 10.9, 11.6, 12.6, 14.2]
        ims = [frame(t).resize((W // 2, H // 2)) for t in ts]
        sheet = Image.new("RGB", (W // 2 * 3, H // 2 * 3))
        for i, im in enumerate(ims): sheet.paste(im, ((i % 3) * W // 2, (i // 3) * H // 2))
        sheet.save(os.path.join(TMP, "texas_stills.png")); print("stills ok"); sys.exit()

    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
                           "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)):
        ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); ff.wait()
    print("video ok", OUT)
