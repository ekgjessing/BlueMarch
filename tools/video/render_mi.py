"""Michigan: "JD, habibi" (Abdul El-Sayed, election night, Detroit, Nov 3 2026).

Audio: C-SPAN, "U.S. Senate Candidate Abdul El-Sayed (D-MI) Election Night Remarks"
https://www.c-span.org/program/campaign-2026/us-senate-candidate-abdul-el-sayed-d-mi-election-night-remarks/687411
Source cut kept locally in lyd/mi-habibi-src555.mp3 (starts at 555.0 s of the C-SPAN audio).
"""
import math, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from puppet import *

SRC = os.path.join(ROOT, "lyd", "mi-habibi-src555.mp3")
SRC0 = 555.0          # file offset in the C-SPAN audio
OFF = 567.1           # video_t = cspan_t - OFF
DUR = 19.5
TMP = os.path.join(ROOT, "video")
os.makedirs(TMP, exist_ok=True)

# ---------------------------------------------------------------- audio
mix = Mix(DUR)
sp = fade(load(SRC, OFF - SRC0, OFF - SRC0 + DUR), 0.25, 1.4)
mix.add(sp, 0.0)
mix.add(sfx_pop(700, 0.16, 0.18), 4.95)
mix.add(sfx_boing(0.45, 0.16), 6.35)
WAV = os.path.join(TMP, "mi_audio.wav"); mix.write(WAV)

# word spans (C-SPAN time) from faster-whisper small.en
WORDS = [(568.38, 568.62), (568.62, 568.92), (572.22, 572.5), (572.5, 572.78), (572.78, 573.1),
         (575.34, 576.22), (576.22, 576.44), (576.44, 576.84), (576.84, 577.2), (577.2, 577.52), (577.52, 578.1),
         (578.1, 579.14), (579.14, 579.28), (579.28, 579.5), (579.5, 579.86), (579.86, 580.9), (580.9, 581.2),
         (581.2, 581.56), (581.56, 582.2), (582.2, 582.42), (582.42, 582.66), (582.66, 582.86), (582.86, 583.02),
         (583.02, 583.14), (583.14, 583.58)]
mouth = Mouth([(a - OFF, b - OFF) for a, b in WORDS])

CAPS = [(1.15, 2.4, "J.D. …"), (5.0, 6.5, "Habibi."),
        (8.15, 13.7, "There is this delicious irony in the fact that you're"),
        (13.7, 17.0, "constitutionally obligated to swear me in in January.")]

# ---------------------------------------------------------------- characters
AS_SKIN, AS_HAIR = (184, 128, 92), (34, 26, 22)
JD_SKIN, JD_HAIR = (240, 200, 176), (62, 44, 32)


def abdul(d, hx, hy, s, t, mo, look=(0, 0), wink=False):
    d.chord(hx, hy - 30 * s, 90 * s, 80 * s, 180, 360, AS_HAIR)               # short hair cap
    puppet_head(d, hx, hy, s, AS_SKIN, mo=mo, look=look, blink=wink, beard=(44, 32, 26), ry=102)
    d.chord(hx, hy - 52 * s, 84 * s, 52 * s, 190, 350, AS_HAIR)               # hairline
    for sx in (-1, 1): d.l([(hx + sx * 52 * s, hy - 40 * s), (hx + sx * 18 * s, hy - 38 * s - (6 * s if mo > 0.3 else 0))], AS_HAIR, 7 * s)


def vance(d, hx, hy, s, t, mo=0.0, look=(0, 0), blush=0.0, brow=0.0, teeth=False):
    puppet_head(d, hx, hy, s, JD_SKIN, mo=mo, look=look, blush=blush, beard=(70, 50, 36), rx=92, ry=104, teeth=teeth)
    d.chord(hx, hy - 50 * s, 96 * s, 66 * s, 180, 360, JD_HAIR)
    d.p([(hx - 96 * s, hy - 50 * s), (hx - 30 * s, hy - 112 * s), (hx + 70 * s, hy - 100 * s), (hx + 96 * s, hy - 52 * s),
         (hx + 30 * s, hy - 78 * s)], JD_HAIR)                                     # side part swoop
    for sx in (-1, 1):
        lift = brow * 14 * s
        d.l([(hx + sx * 56 * s, hy - 40 * s - lift), (hx + sx * 16 * s, hy - 36 * s - lift * (0.4 if sx < 0 else 1.2))], JD_HAIR, 8 * s)


# ---------------------------------------------------------------- backgrounds
rng = np.random.default_rng(5)
bgA = gradient((16, 40, 120), (6, 14, 50))
d0 = D(bgA)
d0.r(160, 40, 1120, 250, (24, 70, 180), 20)
d0.text(640, 120, "MICHIGAN", 96, (255, 255, 255))
d0.text(640, 205, "WE DID IT", 34, (255, 215, 90))
for x in (420, 470, 520, 760, 810, 860): d0.star(x, 203, 15, (255, 215, 90))
bgA = glow(bgA, [(640, 360, 360, 260, (255, 240, 200, 60)), (140, 60, 140, 70, (255, 255, 255, 90)), (1140, 60, 140, 70, (255, 255, 255, 90))])
BALLOONS = [(rng.uniform(30, 1250), rng.uniform(260, 700), rng.choice([0, 1, 2])) for _ in range(9)]
CONF = [(rng.uniform(0, W), rng.uniform(-700, 0), rng.uniform(140, 260), rng.uniform(0, 6.28),
         tuple(int(v) for v in rng.choice([(255, 255, 255), (120, 180, 255), (255, 210, 80)]))) for _ in range(110)]

bgB = gradient((26, 22, 34), (12, 10, 18))
d0 = D(bgB)
d0.r(0, 470, 1280, 720, (60, 40, 46))                         # couch
d0.r(60, 420, 1220, 520, (84, 56, 62), 40)
d0.r(980, 120, 1180, 300, (36, 30, 40), 8, (90, 80, 90), 4)   # picture frame
d0.text(1080, 210, "USA", 40, (150, 50, 60))
bgB = glow(bgB, [(640, 330, 380, 300, (110, 160, 255, 70))])  # TV glow

bgC = gradient((70, 30, 34), (30, 14, 18))
d0 = D(bgC)
for x in range(0, 1280, 160):
    d0.r(x + 20, 80, x + 70, 720, (226, 214, 190)); d0.r(x + 14, 70, x + 76, 92, (240, 230, 210))
d0.r(0, 0, 1280, 70, (40, 60, 130)); d0.text(640, 36, "UNITED STATES SENATE", 30, (255, 220, 120))
bgC = glow(bgC, [(640, 300, 420, 260, (255, 230, 180, 60))])


def crowd(d, t, cheer):
    for k in range(12):
        x = 50 + k * 108 + (k % 3) * 7; y = 700 + (k % 2) * 16
        yy = y - cheer * abs(math.sin(t * 7.5 + k * 1.3)) * 18
        if k % 3 == 0:
            d.l([(x, yy - 30), (x + 10, yy - 140 + 6 * math.sin(t * 5 + k))], (70, 60, 50), 6)
            d.r(x - 40, yy - 200 + 6 * math.sin(t * 5 + k), x + 60, yy - 130 + 6 * math.sin(t * 5 + k), (40, 110, 230), 6, (255, 255, 255), 3)
            d.text(x + 10, yy - 165 + 6 * math.sin(t * 5 + k), "HABIBI" if t > 6 else "MI ♥", 18, (255, 255, 255))
        d.e(x, yy, 48, 56, [(60, 40, 30), (120, 80, 50), (30, 24, 20), (190, 150, 110)][k % 4])


def podium(d):
    d.p([(510, 470), (770, 470), (750, 720), (530, 720)], (30, 52, 120), (14, 30, 80), 3)
    d.r(494, 456, 786, 482, (44, 70, 150), 6)
    d.star(640, 590, 40, (255, 255, 255))
    for x in (622, 658):
        d.l([(x, 458), (x + (x - 640) * 0.4, 405)], (40, 40, 40), 5); d.e(x + (x - 640) * 0.4, 400, 9, 12, (25, 25, 25))


def balloons(d, t):
    for x, y, c in BALLOONS:
        col = [(220, 40, 50), (255, 255, 255), (40, 100, 230)][c]
        yy = y - 8 * math.sin(t * 1.6 + x)
        d.l([(x, yy + 44), (x + 6 * math.sin(t + x), yy + 160)], (200, 200, 200), 2)
        d.e(x, yy, 34, 42, col, shade(col, 0.8), 2)


def confetti(d, t, t0):
    lt = t - t0
    if lt < 0: return
    for x, y0, v, ph, c in CONF:
        y = y0 + v * lt
        if 0 < y < H: d.r(x + 12 * math.sin(lt * 4 + ph), y, x + 12 * math.sin(lt * 4 + ph) + 10, y + 6, c, 2)


def scene_a(t):
    img = bgA.copy(); d = D(img)
    balloons(d, t)
    mo = mouth(t)
    hx, hy, s = 640, 262 - 5 * mo, 1.0
    by = hy + 96
    suit(d, hx, by, s, (30, 34, 52), shirt=(200, 225, 250), tie=None, neck=AS_SKIN)
    # arms: point at "J.D.", heart hands on "Habibi", gesture otherwise
    if t < 2.4:
        p = ease((t - 1.0) / 0.3)
        rh = (lerp(820, 900, p), lerp(560, 300, p)); lh = (470, 560)
    elif 4.9 <= t < 6.6:
        k = ease((t - 4.95) / 0.25)
        lh = (lerp(470, 610, k), lerp(560, 440, k)); rh = (lerp(810, 670, k), lerp(560, 440, k))
    else:
        g = math.sin(t * 3.1) * 18 * (1 if mo > 0 else 0.3)
        lh = (470 + g, 540 - g); rh = (810 - g, 520 + g)
    for h, sx in ((lh, -1), (rh, 1)):
        d.l([(hx + sx * 110, by + 40), ((hx + sx * 110 + h[0]) / 2 + sx * 30, (by + 40 + h[1]) / 2 + 30), h], (30, 34, 52), 46)
    podium(d)
    abdul(d, hx, hy, s, t, mo, look=(0, 0.3) if t < 2.4 else (0, 0), wink=(t > 11.9 and t < 12.4))
    if 4.9 <= t < 6.6:
        k = ease((t - 4.95) / 0.25)
        d.heart(640, 430, 46 * k, (235, 60, 90))
        for i in range(5):
            lt = (t - 5.0 - i * 0.18)
            if lt > 0:
                sx = -1 if i % 2 else 1
                d.heart(640 + sx * (90 + lt * 260 + i * 12), 430 - lt * 180 + 10 * math.sin(lt * 6), 18, (255, 110, 140))
    for h in (lh, rh): hand(d, *h, 1.0, AS_SKIN)
    crowd(d, t, 1.0 if mo == 0 else 0.25)
    z = keyed(t, [(0, 1.0), (2.0, 1.12), (4.9, 1.18), (6.6, 1.18), (8.1, 1.0), (12.9, 1.22)])[0]
    return img, z, 640, 300


def scene_b(t):
    img = bgB.copy(); d = D(img)
    hx, hy, s = 640, 300, 1.05
    by = hy + 100 * s
    suit(d, hx, by, s, (24, 30, 64), tie=(200, 35, 45), neck=JD_SKIN)
    if t < 4.9:     # startled: who said my name?
        k = ease((t - 2.15) / 0.2)
        vance(d, hx, hy - 10 * k, s, t, brow=k, look=(0.8 * math.sin(t * 6) if t > 2.8 else 0, -0.2))
        if t > 2.5:
            p = back((t - 2.5) / 0.3)
            d.text(860, 150, "?", 120 * p + 1, (255, 255, 255), stroke=6, sf=(30, 30, 60))
    else:           # habibi: melt
        k = ease((t - 6.35) / 0.5)
        sway = 10 * math.sin((t - 6.3) * 4) * k
        vance(d, hx + sway, hy + 6 * k, s, t, blush=k, brow=0.6 * k, look=(-0.9 * k, 0.4 * k), teeth=k > 0.5)
        for i in range(7):
            lt = t - 6.4 - i * 0.16
            if lt > 0:
                a = i * 0.9
                d.heart(hx + 170 * math.cos(a + lt * 2), hy - 60 + 120 * math.sin(a + lt * 2) - lt * 40, 22, (240, 80, 120))
    # remote in hand
    rh = (840, 610)
    d.l([(hx + 110 * s, by + 40), (880, 560), rh], (24, 30, 64), 46)
    d.r(rh[0] - 14, rh[1] - 70, rh[0] + 14, rh[1] + 10, (30, 30, 34), 6)
    hand(d, *rh, 1.0, JD_SKIN)
    z = keyed(t, [(2.0, 1.0), (4.9, 1.1), (6.3, 1.0), (8.1, 1.15)])[0] if t < 8.1 else 1.15
    return img, z, 640, 320


def scene_c(t):
    img = bgC.copy(); d = D(img)
    lt = t - 12.9
    # calendar drops in
    cy = lerp(-160, 160, back(lt / 0.5))
    d.l([(640, 0), (640, cy - 90)], (60, 60, 60), 3)
    d.r(530, cy - 90, 750, cy + 90, (250, 250, 245), 10, (180, 180, 180), 3)
    d.r(530, cy - 90, 750, cy - 40, (200, 40, 50), 10)
    d.text(640, cy - 64, "JANUARY", 28, (255, 255, 255))
    d.text(640, cy + 28, "3", 84, (40, 40, 50))
    # Vance holding the book, forced grin
    vx, vy = 360, 330
    suit(d, vx, vy + 100, 0.95, (24, 30, 64), tie=(200, 35, 45), neck=JD_SKIN)
    sweat = lt > 1.0
    vance(d, vx, vy, 0.95, t, teeth=True, brow=0.4, look=(1, 0), blush=0.15)
    if sweat:
        yy = vy - 40 + ((lt * 60) % 60)
        d.e(vx + 92, yy, 9, 13, (140, 200, 255)); d.p([(vx + 84, yy - 4), (vx + 100, yy - 4), (vx + 92, yy - 24)], (140, 200, 255))
    # book between them
    bx, by_ = 560, 520
    d.r(bx - 70, by_ - 20, bx + 70, by_ + 30, (90, 40, 30), 6, (60, 26, 20), 3)
    d.r(bx - 62, by_ - 24, bx + 62, by_ - 14, (240, 230, 200), 3)
    d.l([(vx + 100, 470), (bx - 40, by_ + 20)], (24, 30, 64), 44)
    hand(d, bx - 40, by_ + 26, 0.9, JD_SKIN)
    # Abdul, hand raised on "swear me in"
    ax, ay = 900, 320
    mo = mouth(t)
    suit(d, ax, ay + 98, 0.95, (30, 34, 52), shirt=(200, 225, 250), tie=None, neck=AS_SKIN)
    up = ease((t - 15.3) / 0.35)
    rh = (lerp(1040, 1060, up), lerp(560, 250, up))
    lhd = (bx + 40, by_ - 30)
    d.l([(ax - 100, ay + 140), (760, 470), lhd], (30, 34, 52), 44)
    d.l([(ax + 100, ay + 140), (1060, lerp(500, 330, up)), rh], (30, 34, 52), 44)
    abdul(d, ax, ay - 4 * mo, 0.95, t, mo, look=(-0.8, 0) if t < 16.5 else (0, 0), wink=(17.2 < t < 17.7))
    hand(d, *lhd, 0.9, AS_SKIN)
    hand(d, *rh, 0.95, AS_SKIN)
    confetti(d, t, 16.6)
    z = keyed(t, [(12.9, 1.0), (15.3, 1.06), (16.6, 1.0)])[0]
    return img, z, 640, 360


def frame(t):
    if t < 2.0 or 4.9 <= t < 6.3 or 8.1 <= t < 12.9: img, z, cx, cy = scene_a(t)
    elif t < 8.1: img, z, cx, cy = scene_b(t)
    else: img, z, cx, cy = scene_c(t)
    return compose(img, z, cx, cy, t, CAPS)


if __name__ == "__main__":
    render("mi", frame, DUR, WAV, [1.6, 2.9, 5.5, 7.2, 10.0, 13.6, 15.9, 17.4, 19.0])
