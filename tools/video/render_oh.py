"""Ohio: Trump on Sen. Jon Husted ("He's got these, like, claws"), RNC midterm rally, Youngstown, Oct 11 2026.

Audio: C-SPAN, "President Trump Speaks at RNC Midterm Rally in Ohio"
https://www.c-span.org/program/campaign-2026/president-trump-speaks-at-rnc-midterm-rally-in-ohio/686403
Source cut kept locally in lyd/oh-husted-src530.mp3 (starts at 530.0 s of the C-SPAN audio).
"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from puppet import *

SRC = os.path.join(ROOT, "lyd", "oh-husted-src530.mp3")
DUR = 21.6
TMP = os.path.join(ROOT, "video")
SEGS = [(12.3, 31.5, 0.3), (37.15, 37.95, 19.9)]       # (file_start, file_end, video_start)
def v(x):
    for a, b, t0 in SEGS:
        if a <= x <= b: return x - a + t0
    raise ValueError(x)

mix = Mix(DUR)
for a, b, t0 in SEGS: mix.add(fade(load(SRC, a, b), 0.1, 0.25), t0)
mix.add(sfx_boing(0.4, 0.14), v(23.0) + 0.05)
for k in range(4): mix.add(sfx_snip(0.35), 18.55 + k * 0.32)
for k, s in enumerate(sfx_chime(0.18)): mix.add(s, 20.75 + k * 0.11)
WAV = os.path.join(TMP, "oh_audio.wav"); mix.write(WAV)

WORDS = [(12.5, 12.72), (12.72, 12.92), (12.92, 13.06), (13.06, 13.22), (13.22, 13.42), (13.42, 13.64), (13.64, 13.82),
         (13.82, 14.08), (14.08, 14.4), (14.58, 14.7), (14.7, 15.0), (15.0, 15.6), (15.6, 15.9), (15.9, 16.24),
         (16.26, 17.0), (17.0, 17.24), (17.24, 17.42), (17.42, 17.6), (17.6, 17.72), (17.72, 17.84), (17.84, 17.98),
         (17.98, 18.16), (18.16, 18.6), (19.5, 19.72), (19.72, 19.88), (19.88, 20.14), (20.24, 20.48), (20.48, 20.64),
         (20.64, 20.94), (20.94, 21.3), (21.3, 21.58), (21.58, 21.96), (22.14, 22.2), (22.2, 22.36), (22.36, 22.5),
         (22.5, 22.74), (22.74, 23.08), (23.2, 23.34), (23.34, 23.5), (23.5, 23.68), (23.68, 23.86), (23.86, 24.08),
         (24.08, 24.24), (25.68, 25.94), (25.94, 26.1), (26.1, 26.24), (26.24, 26.44), (26.44, 26.58), (26.58, 26.76),
         (26.76, 27.14), (27.36, 27.5), (27.5, 27.62), (27.62, 27.76), (27.76, 28.02), (28.02, 28.26), (28.26, 28.42),
         (28.42, 28.68), (28.68, 29.2), (30.16, 30.44), (37.3, 37.5), (37.5, 37.7)]
mouth = Mouth([(v(a), v(b)) for a, b in WORDS])

CAPS = [(0.3, 2.3, "And I don't do this with men very often."),
        (2.4, 6.5, "I started examining his body, because I didn't know he was a great athlete."),
        (7.3, 9.8, "And I looked, and I watched up and down."),
        (9.8, 12.2, "I looked at his a**, and I looked at the whole—"),
        (13.5, 15.9, "And then I looked at his hands. Look at his hands."),
        (15.9, 18.4, "He's got these, like… claws."), (19.8, 20.7, "Congratulations.")]
T_ASS = v(22.74)      # ~10.74
T_HANDS = v(25.9)     # ~13.9
T_CLAWS = v(30.1)     # ~18.1

HS_SKIN, HS_HAIR = (238, 192, 160), (196, 196, 200)

bg = gradient((20, 26, 60), (60, 22, 34))
d0 = D(bg)
d0.r(120, 40, 1160, 200, (190, 20, 40), 18); d0.text(640, 105, "OHIO", 86, (255, 255, 255))
d0.text(640, 170, "MIDTERM RALLY", 26, (255, 225, 225))
bg = glow(bg, [(640, 360, 420, 300, (255, 230, 190, 60))])


def crowd(d, t, cheer):
    for k in range(12):
        x = 50 + k * 108 + (k % 3) * 9; y = 708 + (k % 2) * 14
        yy = y - cheer * abs(math.sin(t * 8 + k * 1.3)) * 16
        hc = [(190, 20, 40), (245, 240, 230), (30, 40, 110)][k % 3]
        d.e(x, yy, 50, 58, [(70, 50, 35), (150, 110, 70), (220, 200, 160), (40, 30, 25)][k % 4])
        d.r(x - 40, yy - 98, x + 40, yy - 34, hc, 16); d.e(x, yy - 34, 74, 15, hc)


def husted(d, hx, hy, s, look=(0, 0), blush=0.0, brow=0.0, smile=True, turned=False):
    by = hy + 96 * s
    if turned:     # back view, for the magnifying glass
        d.p([(hx - 118 * s, by), (hx + 118 * s, by), (hx + 150 * s, by + 330), (hx - 150 * s, by + 330)], (34, 40, 70))
        d.r(hx - 24 * s, by - 26 * s, hx + 24 * s, by + 10, HS_SKIN)
        d.e(hx, hy, 88 * s, 100 * s, HS_HAIR, shade(HS_HAIR, 0.8), 4 * s)
        for sx in (-1, 1): d.e(hx + sx * 86 * s, hy + 5 * s, 15 * s, 24 * s, HS_SKIN, shade(HS_SKIN, 0.8), 3 * s)
        d.l([(hx, by + 150 * s), (hx, by + 330)], (24, 28, 52), 6 * s)     # coat vent
        return
    suit(d, hx, by, s, (34, 40, 70), tie=(40, 90, 190), neck=HS_SKIN)
    puppet_head(d, hx, hy, s, HS_SKIN, look=look, blush=blush, teeth=smile, rx=86, ry=100)
    d.chord(hx, hy - 48 * s, 92 * s, 62 * s, 180, 360, HS_HAIR)
    d.p([(hx - 92 * s, hy - 48 * s), (hx - 40 * s, hy - 104 * s), (hx + 60 * s, hy - 104 * s), (hx + 92 * s, hy - 50 * s), (hx - 10 * s, hy - 70 * s)], HS_HAIR)
    for sx in (-1, 1):
        lift = brow * 14 * s
        d.l([(hx + sx * 54 * s, hy - 38 * s - lift), (hx + sx * 16 * s, hy - 36 * s - lift)], shade(HS_HAIR, 0.6), 7 * s)


def claw(d, x, y, s, open_):
    red, dark = (220, 60, 40), (150, 30, 20)
    d.r(x - 26 * s, y, x + 26 * s, y + 90 * s, red, 14 * s, dark, 3 * s)          # forearm
    a = 18 + 30 * open_
    d.pie(x - 8 * s, y - 10 * s, 52 * s, 70 * s, 180 + a, 270, red, dark, 3 * s)  # lower pincer
    d.pie(x + 8 * s, y - 10 * s, 52 * s, 70 * s, 270, 360 - a, red, dark, 3 * s)  # upper pincer
    d.e(x, y + 4 * s, 34 * s, 28 * s, red, dark, 3 * s)


def frame(t):
    img = bg.copy(); d = D(img)
    mo = mouth(t)
    TX, TY, HX, HY_ = 400, 270, 900, 290
    scan = 7.3 <= t < 13.0
    turned = T_ASS - 0.35 <= t < 12.6
    # Husted
    if t < T_HANDS:
        husted(d, HX, HY_, 0.95, look=(-1, 0) if not scan else (-1, 0.6), blush=ease((t - T_ASS) / 0.4) if t > T_ASS else 0,
               brow=0.8 if scan else 0, smile=not scan, turned=turned)
        if not turned:
            for sx in (-1, 1):
                d.l([(HX + sx * 108, HY_ + 130), (HX + sx * 130, HY_ + 260), (HX + sx * 120, HY_ + 330)], (34, 40, 70), 44)
                hand(d, HX + sx * 120, HY_ + 340, 0.85, HS_SKIN)
    else:
        husted(d, HX, HY_, 0.95, look=(0, -0.2), brow=1.0 if t > T_CLAWS else 0.3, smile=t < T_CLAWS, blush=0.3)
        up = ease((t - T_HANDS) / 0.4)
        for sx in (-1, 1):
            hxp, hyp = HX + sx * 150, lerp(HY_ + 330, HY_ + 40, up)
            d.l([(HX + sx * 108, HY_ + 130), (HX + sx * 160, HY_ + 200), (hxp, hyp + 40)], (34, 40, 70), 44)
            if t >= T_CLAWS:
                k = back((t - T_CLAWS) / 0.3)
                claw(d, hxp, hyp - 10, 0.9 * k + 0.1, abs(math.sin((t - T_CLAWS) * 9.8)))
            else:
                hand(d, hxp, hyp, 0.9, HS_SKIN)
        if t >= T_CLAWS and t < 19.9:
            p = back((t - T_CLAWS - 0.3) / 0.3)
            d.text(HX + 200, 250, "snip snip", 1 + 44 * p, (255, 225, 60), stroke=4, sf=(40, 20, 20))
    # Trump at the podium
    by = TY + 95
    d.r(TX - 26, TY + 70, TX + 26, by + 10, SK)
    d.p([(TX - 120, by), (TX + 120, by), (TX + 150, by + 320), (TX - 150, by + 320)], SUIT)
    d.p([(TX - 40, by), (TX + 40, by), (TX, by + 90)], (245, 245, 245))
    d.p([(TX - 14, by + 10), (TX + 14, by + 10), (TX + 22, by + 270), (TX, by + 300), (TX - 22, by + 270)], (210, 35, 42))
    trump_head(d, TX, TY - 5 * mo, 1.0, mo, wink=19.95 <= t < 20.5)
    # magnifying glass
    if 2.4 <= t < 13.0:
        k = ease((t - 2.4) / 0.5)
        if scan:
            sy = HY_ + 160 + 150 * math.sin((t - 7.3) * 2.4) if t < T_ASS - 0.35 else HY_ + 250
            gx, gy = lerp(TX + 150, HX - 10, ease((t - 7.0) / 0.4)), sy
        else:
            gx, gy = TX + 170, lerp(TY + 300, TY + 120, k)
        d.l([(TX + 112, by + 40), (gx - 70, gy + 90)], SUIT, 46)
        d.l([(gx - 40, gy + 50), (gx - 90, gy + 110)], (90, 60, 40), 16)
        big_hand(d, gx - 90, gy + 110, 0.8)
        d.e(gx, gy, 66, 66, (200, 230, 255), (60, 60, 70), 10)
        d.e(gx - 18, gy - 20, 18, 12, (255, 255, 255))
    else:
        d.l([(TX + 112, by + 40), (TX + 160, by + 200)], SUIT, 46); big_hand(d, TX + 160, by + 220, 1.0)
    d.l([(TX - 112, by + 40), (TX - 160, by + 200)], SUIT, 46); big_hand(d, TX - 160, by + 220, 1.0)
    # podium
    d.p([(TX - 120, 500), (TX + 120, 500), (TX + 100, 720), (TX - 100, 720)], (92, 58, 40), (60, 38, 26), 3)
    d.r(TX - 136, 486, TX + 136, 508, (122, 80, 54), 6)
    d.e(TX, 600, 44, 44, (30, 70, 160), (240, 240, 240), 4); d.star(TX, 603, 28, (245, 245, 245))
    if turned and t > T_ASS:
        p = back((t - T_ASS) / 0.25)
        d.text(HX + 150, 230, "!", 1 + 120 * p, (255, 240, 120), stroke=6, sf=(40, 20, 20))
    crowd(d, t, 1.0 if (mo == 0 and (t < 0.4 or 18.6 < t)) else 0.2)
    z, cx, cy = keyed(t, [(0, 1.0, 640, 360), (2.3, 1.0, 640, 360), (2.8, 1.12, 560, 330), (6.6, 1.12, 560, 330),
                          (7.3, 1.2, 820, 380), (12.4, 1.2, 820, 380), (13.2, 1.0, 640, 360), (17.8, 1.0, 640, 360),
                          (18.2, 1.25, 900, 300), (19.7, 1.25, 900, 300), (19.95, 1.0, 640, 360)])
    return compose(img, z, cx, cy, t, CAPS)


if __name__ == "__main__":
    render("oh", frame, DUR, WAV, [1.2, 4.5, 8.2, 11.2, 14.6, 16.8, 18.6, 19.4, 20.3])
