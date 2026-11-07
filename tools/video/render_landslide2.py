import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_texas as T

D, SS, W, H, FPS, SR = T.D, T.SS, T.W, T.H, T.FPS, T.SR
font, FB, FR, ease, lerp, back, keyed = T.font, T.FB, T.FR, T.ease, T.lerp, T.back, T.keyed
SRC = "/Users/eirik/Downloads/Trump_ Winning the Election in a Landslide.mp4"
OUT = os.path.join(T.OUTDIR, "landslide-v2-utkast.mp4")
TMP = T.TMP
A0 = 0.5            # source audio starts at this video time
SLIDE = 15.25 + A0  # "landslide"
OVER = 18.7
DUR = 21.4

CAPS = [(0.0, 1.0, "The problem is,"), (1.0, 2.75, "if I'm not running, if I'm not on the ballot,"),
        (2.75, 4.2, "they think, \"Oh, I'm not running.\""), (4.2, 6.4, "And if they like me, and they do like me,"),
        (6.4, 9.0, "I mean, I have polls that show me I'm very popular."), (9.0, 11.1, "You know, you have a lot of fake polls."),
        (11.1, 12.2, "But they like me."), (12.2, 13.5, "Here's the story:"), (13.5, 14.7, "if they get out and vote,"),
        (14.7, 15.87, "we win in a landslide.")]
CAPS = [(a + A0, b + A0, s) for a, b, s in CAPS]

# ---------------------------------------------------------------- audio
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
sp = np.frombuffer(raw, np.float32).copy()
tt = np.arange(len(sp)) / SR
sp *= np.clip(tt / 0.05, 0, 1) * np.clip((tt[-1] - tt) / 0.15, 0, 1)
hop = SR // FPS
rms = np.array([np.sqrt(np.mean(sp[i:i + hop] ** 2)) for i in range(0, len(sp), hop)])
rms = rms / np.percentile(rms, 95)
mouth_env = np.clip((rms - 0.2) / 0.7, 0, 1)
mouth_env = np.convolve(mouth_env, [0.25, 0.5, 0.25], "same")

def mouth(t):
    i = int((t - A0) * FPS)
    return float(mouth_env[i]) if 0 <= i < len(mouth_env) else 0.0

mix = np.zeros(int(DUR * SR) + 1, np.float32)
def add(sig, t0):
    i = int(t0 * SR); m = min(len(sig), len(mix) - i); mix[i:i + m] += sig[:m]
add(sp, A0)
rng = np.random.default_rng(11)
rt = np.arange(int(1.9 * SR)) / SR
rum = np.convolve(rng.uniform(-1, 1, len(rt)), np.ones(180) / 180, "same") * 9
env = np.minimum(1, rt / 0.25) * np.clip((1.9 - rt) / 0.6, 0, 1)
add((rum * env * 0.8 + np.sin(2 * np.pi * 42 * rt) * env * 0.3).astype(np.float32), SLIDE + 0.1)
ct = np.arange(int(0.05 * SR)) / SR
for k in range(28):
    add((rng.uniform(-1, 1, len(ct)) * np.exp(-ct * 90) * rng.uniform(0.1, 0.3)).astype(np.float32), SLIDE + 0.3 + rng.uniform(0, 1.4))
for k, f in enumerate([392.0, 370.0, 349.2, 329.6]):
    d = 1.1 if k == 3 else 0.36
    t2 = np.arange(int(d * SR)) / SR
    vib = 1 + (0.012 * np.sin(2 * np.pi * 6 * t2) if k == 3 else 0)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    tone = sum(np.sin(ph * h) / h for h in range(1, 7)) * np.minimum(1, t2 / 0.03) * np.exp(-t2 * (1.2 if k == 3 else 2.5)) * 0.2
    add(tone.astype(np.float32), OVER + 0.15 + k * 0.38)
mix *= min(1.0, 0.95 / max(1e-6, np.abs(mix).max()))
wav = os.path.join(TMP, "landslide2_audio.wav")
with wave.open(wav, "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((mix * 32767).astype(np.int16).tobytes())

# ---------------------------------------------------------------- background: tarmac + plane
bg = T.gradient((168, 190, 218), (246, 214, 196))
d = D(bg)
d.r(0, 430, W, H, (118, 122, 130)); d.r(0, 600, W, 612, (225, 190, 60))
d.p([(1010, 560), (1080, 560), (1290, 160), (1230, 160)], (150, 155, 165), (110, 115, 125), 3)
for k in range(9):
    y = 545 - k * 44; x = 1020 + (545 - y) * 0.53
    d.l([(x, y), (x + 62, y)], (110, 115, 125), 4)
d.e(500, -70, 800, 250, (40, 64, 130))
d.e(500, -84, 800, 240, (236, 236, 240))
d.e(500, -96, 800, 226, (225, 228, 235))
for k in range(16):
    x = 40 + k * 62; y = 104 + 0.00009 * (x - 500) ** 2 * -1
    d.e(x, y, 11, 14, (60, 70, 90))
for sx, x in ((1, 175), (-1, 1135)):
    d.p([(x - 34, 420), (x + 34, 420), (x + 40, 560), (x - 40, 560)], (28, 30, 38))
    d.e(x, 392, 26, 30, (222, 170, 130)); d.r(x - 22, 382, x + 22, 394, (15, 15, 20), 4)
    d.e(x, 372, 26, 14, (60, 50, 40))
    d.p([(x - 30, 560), (x - 8, 560), (x - 10, 640), (x - 30, 640)], (28, 30, 38))
    d.p([(x + 8, 560), (x + 30, 560), (x + 30, 640), (x + 10, 640)], (28, 30, 38))
bg = bg.filter(ImageFilter.GaussianBlur(2.2 * SS))
bgOver = T.gradient((120, 16, 24), (36, 6, 12))

# rocks
ROCKS = []
for k in range(170):
    x = float(np.clip(rng.normal(640, 210), 260, 1020))
    top = 720 - 520 * math.exp(-((x - 640) / 250) ** 2)
    y = rng.uniform(top + 15, 760)
    r = rng.uniform(26, 62)
    n = rng.integers(6, 9)
    pts = [(math.cos(2 * math.pi * i / n + rng.uniform(-0.2, 0.2)) * r * rng.uniform(0.75, 1.1),
            math.sin(2 * math.pi * i / n + rng.uniform(-0.2, 0.2)) * r * rng.uniform(0.75, 1.1)) for i in range(n)]
    col = tuple(int(c) for c in rng.choice([(120, 108, 96), (140, 124, 104), (98, 90, 84), (156, 140, 118), (110, 96, 78)]))
    ROCKS.append([x, y, pts, col, rng.uniform(-300, 400), rng.uniform(150, 450)])
ROCKS.sort(key=lambda r: -r[1])
for i, rk in enumerate(ROCKS):
    rk.append(SLIDE + 0.15 + i / len(ROCKS) * 1.15)

def rocks(d, t):
    for x, y, pts, col, dx, dy, t0 in ROCKS:
        f = (t - t0) / 0.5
        if f <= 0: continue
        f = min(1, f)
        g = f * f
        px, py = lerp(x + 420 + dx, x, g), lerp(-120 - dy, y, g)
        if f >= 1: py += -10 * math.sin(min(1, (t - t0 - 0.5) / 0.15) * math.pi) * (t - t0 - 0.5 < 0.15)
        d.p([(px + a, py + b) for a, b in pts], col, tuple(max(0, c - 40) for c in col), 3)

# ---------------------------------------------------------------- puppet
def cap(d, hx, hy, s, tilt=0):
    d.chord(hx, hy - 64 * s, 102 * s, 76 * s, 180, 360, (248, 248, 250), (190, 190, 200), 3 * s)
    d.text(hx, hy - 100 * s, "USA", font(FB, int(32 * s * SS)), (30, 40, 90))
    d.e(hx + 34 * s, hy - 62 * s + tilt, 92 * s, 17 * s, (240, 240, 244), (190, 190, 200), 3 * s)

def chart(d, cx, cy, s=1.0, rot=0):
    lay = Image.new("RGBA", (300 * SS, 420 * SS), (0, 0, 0, 0)); c = D(lay)
    c.r(30, 210, 270, 400, (250, 250, 250), 10, (120, 80, 50), 8)
    for k, h in enumerate((40, 60, 35)):
        c.r(60 + k * 46, 380 - h, 92 + k * 46, 380, (150, 150, 160))
    c.r(200, 10, 240, 380, (40, 100, 230))
    c.d.polygon([(220 * SS, 0), (190 * SS, 40 * SS), (250 * SS, 40 * SS)], fill=(40, 100, 230))
    c.r(140, 395, 160, 420, (120, 80, 50))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    if s != 1: lay = lay.resize((int(lay.width * s), int(lay.height * s)), Image.LANCZOS)
    d.img.paste(lay, (int(cx * SS - lay.width / 2), int(cy * SS - lay.height / 2)), lay)

PHR = [(0, "open"), (2.75 + A0, "shrug"), (4.2 + A0, "heart"), (6.4 + A0, "chart"), (9.0 + A0, "fling"),
       (11.1 + A0, "heart"), (12.2 + A0, "finger"), (14.7 + A0, "wide")]
def pose(t, hx, hy, by):
    bob = 6 * math.sin(t * 5)
    P = {"open": [(hx - 215, by + 150 + bob), (hx + 215, by + 150 - bob)],
         "shrug": [(hx - 240, by + 80), (hx + 240, by + 80)],
         "heart": [(hx - 38, by + 95), (hx + 38, by + 95)],
         "chart": [(hx + 110, by + 70), (hx + 235, by + 120)],
         "fling": [(hx - 170, by + 230), (hx - 160, hy - 90)],
         "finger": [(hx - 165, by + 230), (hx + 175, hy - 10 + bob)],
         "wide": [(hx - 300, hy - 40), (hx + 300, hy - 40)]}
    i = max(k for k, (t0, _) in enumerate(PHR) if t0 <= t)
    cur = P[PHR[i][1]]
    if i > 0 and t - PHR[i][0] < 0.3:
        prv = P[PHR[i - 1][1]]; x = ease((t - PHR[i][0]) / 0.3)
        cur = [(lerp(a[0], b[0], x), lerp(a[1], b[1], x)) for a, b in zip(prv, cur)]
    return cur

def puppet(img, d, t):
    hx, hy, s = 640, 268, 1.0
    if t >= SLIDE: hy += 8 * ease((t - SLIDE) / 1.5)
    mo = mouth(t)
    if SLIDE + 0.4 < t: mo = 0.85
    by = hy + 95
    lh, rh = pose(t, hx, hy, by)
    if t > SLIDE + 0.5:
        f = ease((t - SLIDE - 0.5) / 0.4)
        lh = (lerp(lh[0], hx - 200, f), lerp(lh[1], by + 170, f)); rh = (lerp(rh[0], hx + 200, f), lerp(rh[1], by + 170, f))
    d.r(hx - 26, hy + 70, hx + 26, by + 10, T.SK)
    d.p([(hx - 125, by), (hx + 125, by), (hx + 160, 760), (hx - 160, 760)], T.SUIT)
    d.p([(hx - 46, by - 4), (hx + 46, by - 4), (hx + 28, by + 260), (hx - 28, by + 260)], (245, 246, 250))
    d.p([(hx - 46, by - 4), (hx, by + 40), (hx + 46, by - 4), (hx, by + 22)], (225, 228, 236))
    d.p([(hx - 46, by), (hx - 28, by + 260), (hx - 70, by + 230), (hx - 80, by + 40)], (26, 34, 60))
    d.p([(hx + 46, by), (hx + 28, by + 260), (hx + 70, by + 230), (hx + 80, by + 40)], (26, 34, 60))
    for (h, sx) in ((lh, -1), (rh, 1)):
        el = (hx + sx * 175, by + 150) if h[1] > by else (hx + sx * 200, by + 40)
        d.l([(hx + sx * 112, by + 30), el, h], T.SUIT, 48)
    T.trump_head(d, hx, hy, s, mo, False)
    if t < SLIDE + 1.3: cap(d, hx, hy, s)
    ch_in = back((t - (6.4 + A0)) / 0.35)
    if 6.4 + A0 <= t < 9.0 + A0 and ch_in > 0.01:
        chart(d, rh[0], rh[1] - 120 * ch_in, ch_in)
    elif 9.0 + A0 <= t < 10.0 + A0:
        f = ease((t - 9.0 - A0) / 0.9)
        chart(d, lerp(hx + 235, -150, f), lerp(by - 0, -250, f) + 200 * math.sin(f * math.pi) * -1, 1.0 - 0.4 * f, rot=int(260 * f))
    for h in (lh, rh): T.big_hand(d, *h, 1.2)
    # boom mics
    for (p0, p1) in (((-20, 760), (470, 545)), ((1300, 740), (820, 585))):
        d.l([p0, p1], (25, 25, 28), 10)
        mx, my = p1; ux, uy = (p1[0] - p0[0]), (p1[1] - p0[1]); L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
        d.l([(mx - ux * 30, my - uy * 30), (mx + ux * 70, my + uy * 70)], (70, 72, 78), 52)
        for k in range(6):
            q = -20 + k * 16
            d.l([(mx + ux * q - uy * 22, my + uy * q + ux * 22), (mx + ux * q + uy * 22, my + uy * q - ux * 22)], (45, 46, 52), 3)
    return hx, hy, s

def scene_main(t):
    img = bg.copy(); d = D(img); d.img = img
    hx, hy, s = puppet(img, d, t)
    rocks(d, t)
    if t >= SLIDE + 1.3:
        wob = 6 * math.sin((t - SLIDE) * 9) * max(0, 1 - (t - SLIDE - 1.3) / 1.0)
        cap(d, hx, hy + 6, s, wob)
    shake = 9 * min(1, max(0, (t - SLIDE - 0.1) / 0.3)) * max(0, 1 - (t - SLIDE - 1.4) / 0.6) if t > SLIDE else 0
    z = 1.0 + 0.06 * ease((t - (12.2 + A0)) / 2.5) - 0.06 * ease((t - SLIDE) / 0.6)
    return img, z, 640 + shake * math.sin(t * 83), 340 + shake * math.cos(t * 67)

def scene_over(t):
    img = bgOver.copy()
    lt = t - OVER
    k = back(lt / 0.4)
    if k > 0.01:
        card = Image.new("RGBA", (700 * SS, 420 * SS), (0, 0, 0, 0)); c = D(card)
        c.r(4, 4, 696, 416, (28, 10, 14), 32, (230, 50, 60), 6)
        c.text(350, 100, "GAME OVER", font(FB, 82 * SS), (255, 255, 255))
        c.text(350, 180, "You stepped into a red state.", font(FR, 30 * SS), (255, 200, 205))
        c.text(350, 228, "Route: 6 states · Clips: 6 / 48", font(FR, 24 * SS), (210, 170, 175))
        b = back((lt - 0.8) / 0.35)
        if b > 0.01:
            bw, bh = 300 * b, 74 * b
            c.r(350 - bw / 2, 320 - bh / 2, 350 + bw / 2, 320 + bh / 2, (40, 100, 230), 37 * b)
            if b > 0.6: c.text(350, 320, "TRY AGAIN", font(FB, int(30 * b) * SS), (255, 255, 255))
        cw, ch = int(card.width * k), int(card.height * k)
        card = card.resize((cw, ch), Image.LANCZOS)
        img.paste(card, (int(640 * SS - cw / 2), int(360 * SS - ch / 2)), card)
    return img, 1.0, 640, 360

FCAP = font(FR, 28); FWM = font(FR, 17)
def frame(t):
    img, z, cx, cy = scene_main(t) if t < OVER else scene_over(t)
    cw, ch = W * SS / z, H * SS / z
    x0 = min(max(cx * SS - cw / 2, 0), W * SS - cw); y0 = min(max(cy * SS - ch / 2, 0), H * SS - ch)
    out = img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.text((18, 14), "DRAFT · animatic", font=FWM, fill=(255, 255, 255, 170))
    for a, b, txt in CAPS:
        if a <= t < b:
            tw = od.textlength(txt, font=FCAP)
            od.rounded_rectangle([640 - tw / 2 - 22, 632, 640 + tw / 2 + 22, 684], 12, fill=(0, 0, 0, 175))
            od.text((640, 658), txt, font=FCAP, fill=(255, 255, 255), anchor="mm")
    return Image.alpha_composite(out, ov).convert("RGB")

if "--stills" in sys.argv:
    ts = [1.5, 5.5, 8.0, 9.9, 15.8, 16.6, 17.4, 18.3, 19.8]
    ims = [frame(t).resize((W // 2, H // 2)) for t in ts]
    sheet = Image.new("RGB", (W // 2 * 3, H // 2 * 3))
    for i, im in enumerate(ims): sheet.paste(im, ((i % 3) * W // 2, (i // 3) * H // 2))
    sheet.save(os.path.join(TMP, "landslide2_stills.png")); print("stills ok"); sys.exit()

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
                       "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for i in range(int(DUR * FPS)):
    ff.stdin.write(frame(i / FPS).tobytes())
ff.stdin.close(); ff.wait()
print("video ok", OUT)
