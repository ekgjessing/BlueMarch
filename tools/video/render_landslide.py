import math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render_texas as T

D, SS, W, H, FPS, SR = T.D, T.SS, T.W, T.H, T.FPS, T.SR
font, FB, FR, ease, lerp, back = T.font, T.FB, T.FR, T.ease, T.lerp, T.back
DUR = 15.0
OUT = os.path.join(T.OUTDIR, "landslide-utkast.mp4")
TMP = T.TMP

# ---------------------------------------------------------------- text + timing
SEGS = [("I wasn't on the Ballot and if I was, we would have won ", 1.8, 0.068),
        ("IN A LANDSLIDE!", 6.0, 0.05),
        (" Thank you for your attention to this matter.", 7.6, 0.052),
        ("\nPresident DONALD J. TRUMP", 10.2, 0.038)]
FULL, CT = "", []
for txt, t0, dt in SEGS:
    for i, ch in enumerate(txt):
        FULL += ch; CT.append(t0 + i * dt)
CT = np.array(CT)
BOOM, SEND, OVER = 6.8, 11.6, 12.0

def typed(t): return int((CT <= t).sum())
def last_key(t):
    k = typed(t); return CT[k - 1] if k else -9

F_POST = font(FR, 29 * SS)
TEXT_W = 530 * SS
def wrap(text):
    lines, start, i = [], 0, 0
    while i < len(text):
        if text[i] == "\n":
            lines.append((start, i)); start = i + 1; i += 1; continue
        j = text.find(" ", i + 1)
        j = len(text) if j == -1 else j
        nl = text.find("\n", i + 1)
        if nl != -1 and nl < j: j = nl
        if F_POST.getlength(text[start:j]) > TEXT_W and i > start:
            lines.append((start, i)); start = i + 1 if text[i] == " " else i
        i = j
    lines.append((start, len(text)))
    return lines
LINES = wrap(FULL)

# ---------------------------------------------------------------- audio
mix = np.zeros(int(DUR * SR) + 1, np.float32)
def add(sig, t0):
    i = int(t0 * SR); m = min(len(sig), len(mix) - i); mix[i:i + m] += sig[:m]
rng = np.random.default_rng(7)
kt = np.arange(int(0.035 * SR)) / SR
for ch, t in zip(FULL, CT):
    if ch in " \n": continue
    amp = rng.uniform(0.18, 0.3)
    add((rng.uniform(-1, 1, len(kt)) * np.exp(-kt * 160) * amp + np.sin(2 * np.pi * 1800 * kt) * np.exp(-kt * 220) * amp * 0.5).astype(np.float32), t)
bt = np.arange(int(0.9 * SR)) / SR
add((np.sin(2 * np.pi * 55 * bt) * np.exp(-bt * 5) * 0.9 + rng.uniform(-1, 1, len(bt)) * np.exp(-bt * 14) * 0.35).astype(np.float32), BOOM)
wt = np.arange(int(0.45 * SR)) / SR
noise = np.convolve(rng.uniform(-1, 1, len(wt)), np.ones(12) / 12, "same")
add((noise * np.sin(np.pi * wt / 0.45) ** 2 * 0.8).astype(np.float32), SEND)
for k, f in enumerate([392.0, 370.0, 349.2, 329.6]):
    d = 1.1 if k == 3 else 0.36
    tt = np.arange(int(d * SR)) / SR
    vib = 1 + (0.012 * np.sin(2 * np.pi * 6 * tt) if k == 3 else 0)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    tone = sum(np.sin(ph * h) / h for h in range(1, 7)) * np.minimum(1, tt / 0.03) * np.exp(-tt * (1.2 if k == 3 else 2.5)) * 0.22
    add(tone.astype(np.float32), OVER + 0.15 + k * 0.38)
mix *= min(1.0, 0.95 / max(1e-6, np.abs(mix).max()))
wav = os.path.join(TMP, "landslide_audio.wav")
with wave.open(wav, "wb") as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((mix * 32767).astype(np.int16).tobytes())

# ---------------------------------------------------------------- backgrounds
bg = T.gradient((84, 60, 24), (26, 18, 10))
d = D(bg)
for k in range(14):
    x = k * 96
    d.r(x, 0, x + 48, H, (100, 74, 30))
dark = Image.new("RGB", bg.size, (0, 0, 0)); bg = Image.blend(bg, dark, 0.25)
glow = Image.new("RGBA", bg.size, (0, 0, 0, 0)); gd = D(glow)
gd.e(330, 380, 260, 260, (255, 220, 140, 60)); gd.e(920, 350, 380, 260, (180, 210, 255, 45))
bg = Image.alpha_composite(bg.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(70 * SS))).convert("RGB")
bgOver = T.gradient((120, 16, 24), (36, 6, 12))

# stamp layer
stamp = Image.new("RGBA", (760 * SS, 170 * SS), (0, 0, 0, 0)); sd = D(stamp)
sd.r(10, 10, 750, 160, None, 18, (225, 30, 40), 10)
sd.text(380, 86, "IN A LANDSLIDE!", font(FB, 76 * SS), (225, 30, 40), stroke=3, sf=(255, 255, 255))
stamp = stamp.rotate(8, resample=Image.BICUBIC, expand=True)

# ---------------------------------------------------------------- scene
SKIN = T.SK
def puppet(d, t):
    hx, hy, s = 330, 290, 1.0
    boom = 1.0 - ease((t - BOOM) / 0.6) if t >= BOOM else 0.0
    hy -= 16 * boom
    since = t - last_key(t)
    mo = 0.35 * max(0.0, 1 - since / 0.09) if t < SEND else 0.0
    if BOOM - 0.75 <= t < BOOM + 0.5: mo = 0.9
    by = hy + 95 * s
    d.r(150, 190, 510, 720, (205, 160, 60), 40, (150, 110, 35), 6)
    d.r(180, 220, 480, 720, (160, 30, 40), 30)
    d.r(hx - 26, hy + 70, hx + 26, by + 10, SKIN)
    d.p([(hx - 120, by), (hx + 120, by), (hx + 150, by + 330), (hx - 150, by + 330)], T.SUIT)
    d.p([(hx - 40, by), (hx + 40, by), (hx, by + 90)], (245, 245, 245))
    d.p([(hx - 14, by + 10), (hx + 14, by + 10), (hx + 22, by + 270), (hx, by + 300), (hx - 22, by + 270)], (210, 35, 42))
    tap = max(0.0, 1 - since / 0.07) if t < SEND else 0
    send_lift = ease((t - (SEND - 0.35)) / 0.2) - ease((t - SEND) / 0.25) if SEND - 0.35 < t < SEND + 0.4 else 0
    phone = (400, 560)
    lh = (phone[0] - 50, phone[1] + 50)
    rh = (phone[0] + 40, phone[1] - 50 + 14 * tap - 40 * send_lift)
    if boom > 0.3: rh = (rh[0] + 40, rh[1] - 60 * boom)
    d.l([(hx - 112, by + 30), (hx - 150, by + 190), lh], T.SUIT, 48)
    d.l([(hx + 112, by + 30), (hx + 180, by + 170), rh], T.SUIT, 48)
    T.trump_head(d, hx, hy, s, mo, False)
    d.r(phone[0] - 34, phone[1] - 62, phone[0] + 34, phone[1] + 62, (20, 20, 24), 12)
    d.r(phone[0] - 28, phone[1] - 52, phone[0] + 28, phone[1] + 52, (150, 190, 255), 6)
    T.big_hand(d, *lh, 1.2)
    T.big_hand(d, *rh, 1.2)

def post_card(t):
    card = Image.new("RGBA", (620 * SS, 470 * SS), (0, 0, 0, 0)); c = D(card)
    c.r(4, 4, 616, 466, (255, 255, 255), 28, (210, 210, 215), 3)
    c.e(56, 56, 34, 34, (230, 236, 248))
    T.trump_head(c, 56, 64, 0.27)
    c.text(108, 44, "Donald J. Trump", font(FB, 24 * SS), (20, 20, 25), anchor="lm")
    c.text(108, 74, "@realDonaldTrump", font(FR, 20 * SS), (120, 120, 130), anchor="lm")
    n = typed(t)
    y = 128
    for a, b in LINES:
        if n <= a: break
        seg = FULL[a:min(b, n)]
        c.text(36, y, seg, F_POST, (25, 25, 30), anchor="lm")
        y += 42
    if t < SEND and (int(t * 3) % 2 == 0 or t - last_key(t) < 0.4):
        a, b = next(((a, b) for a, b in LINES if a <= max(n - 1, 0) <= b), LINES[0])
        cx = 36 * SS + F_POST.getlength(FULL[a:min(b, n)])
        cy = 128 + 42 * [l for l in LINES].index((a, b))
        c.d.rectangle([cx + 4, (cy - 16) * SS, cx + 4 + 3 * SS, (cy + 16) * SS], fill=(40, 100, 230))
    c.text(36, 432, "Nov 04, 2026, 9:07 AM", font(FR, 19 * SS), (120, 120, 130), anchor="lm")
    if t >= SEND - 0.1:
        c.text(584, 432, "Posted", font(FB, 19 * SS), (40, 140, 70), anchor="rm")
    return card

def scene_post(t):
    img = bg.copy(); d = D(img)
    puppet(d, t)
    card = post_card(t)
    fly = ease((t - SEND) / 0.4)
    cx, cy = 910 * SS, (370 - 700 * fly ** 2) * SS
    pop = back((t - 1.2) / 0.4)
    if pop > 0.01:
        cw, ch = int(card.width * pop), int(card.height * pop)
        cc = card.resize((cw, ch), Image.LANCZOS)
        img.paste(cc, (int(cx - cw / 2), int(cy - ch / 2)), cc)
    if BOOM <= t < 7.6:
        k = back((t - BOOM) / 0.25)
        fade = 1 - ease((t - 7.3) / 0.3)
        sw, sh = int(stamp.width * 0.8 * k), int(stamp.height * 0.8 * k)
        if sw > 2 and fade > 0.02:
            st = stamp.resize((sw, sh), Image.LANCZOS)
            st.putalpha(st.getchannel("A").point(lambda a: int(a * fade)))
            img.paste(st, (int(cx - sw / 2), int(cy + 70 * SS - sh / 2)), st)
    z = 1.0 + 0.1 * ease((t - BOOM) / 0.3) - 0.1 * ease((t - (SEND - 0.6)) / 0.5)
    shake = 12 * max(0.0, 1 - (t - BOOM) / 0.5) if t >= BOOM else 0
    return img, z, 700 + shake * math.sin(t * 90), 360 + shake * math.cos(t * 70)

def scene_over(t):
    img = bgOver.copy(); d = D(img)
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

FWM = font(FR, 17)
def frame(t):
    img, z, cx, cy = scene_post(t) if t < OVER else scene_over(t)
    cw, ch = W * SS / z, H * SS / z
    x0 = min(max(cx * SS - cw / 2, 0), W * SS - cw); y0 = min(max(cy * SS - ch / 2, 0), H * SS - ch)
    out = img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.text((18, 14), "DRAFT · animatic", font=FWM, fill=(255, 255, 255, 150))
    return Image.alpha_composite(out, ov).convert("RGB")

if "--stills" in sys.argv:
    ts = [1.4, 3.5, 5.9, 6.9, 7.6, 10.6, 11.75, 12.3, 13.6]
    ims = [frame(t).resize((W // 2, H // 2)) for t in ts]
    sheet = Image.new("RGB", (W // 2 * 3, H // 2 * 3))
    for i, im in enumerate(ims): sheet.paste(im, ((i % 3) * W // 2, (i // 3) * H // 2))
    sheet.save(os.path.join(TMP, "landslide_stills.png")); print("stills ok"); sys.exit()

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-i", wav, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
                       "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for i in range(int(DUR * FPS)):
    ff.stdin.write(frame(i / FPS).tobytes())
ff.stdin.close(); ff.wait()
print("video ok", OUT)
