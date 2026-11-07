"""Kentucky: "It's garbage day in Kentucky" (Nate Morris for Senate, launch ad, June 27 2025).

Audio: https://x.com/NateMorris/status/1938568186133127227 (kept locally in lyd/ky-garbage-day.mp4).
Only the light lines are used. The tag is the real ending: Morris left the race and Trump
picked him for ambassador to Colombia (June 2026).
"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from puppet import *

SRC = os.path.join(ROOT, "lyd", "ky-garbage-day.mp4")
DUR = 20.5
TMP = os.path.join(ROOT, "video")
SEGS = [(2.6, 8.9, 0.3), (15.0, 19.6, 6.9), (39.2, 41.1, 11.8)]
def v(x):
    for a, b, t0 in SEGS:
        if a <= x <= b: return x - a + t0
    raise ValueError(x)

T_TOSS, T_BAG, T_GRAB, T_DROP = 4.5, 11.2, 14.4, 15.7

mix = Mix(DUR)
for a, b, t0 in SEGS: mix.add(fade(load(SRC, a, b), 0.1, 0.25), t0)
rng = np.random.default_rng(11)
def crunch(d=0.45, g=0.35):
    n = int(d * SR); x = rng.uniform(-1, 1, n) * np.exp(-np.arange(n) / SR * 7) * g
    return np.convolve(x, np.ones(30) / 30, "same").astype(np.float32)
mix.add(crunch(), T_TOSS + 0.55); mix.add(crunch(0.3, 0.25), T_BAG + 0.45); mix.add(crunch(0.6, 0.45), T_DROP)
mix.add(sfx_boing(0.4, 0.16), T_GRAB)
t_h = np.arange(int(0.5 * SR)) / SR
mix.add((np.sign(np.sin(2 * np.pi * 220 * t_h)) * 0.06 * np.clip((0.5 - t_h) / 0.1, 0, 1)).astype(np.float32), 16.3)   # horn
for k, s in enumerate(sfx_chime(0.18)): mix.add(s, 17.4 + k * 0.11)
WAV = os.path.join(TMP, "ky_audio.wav"); mix.write(WAV)

PHRASES = [(2.84, 4.6), (5.0, 8.6), (15.04, 15.64), (16.06, 17.6), (17.64, 19.32), (39.32, 40.94)]
sp = []
for a, b in PHRASES:
    n = max(1, int((b - a) / 0.2))
    for i in range(n): sp.append((v(a) + (b - a) * i / n, v(a) + (b - a) * (i + 1) / n))
mouth = Mouth(sp)

CAPS = [(0.4, 2.6, "It's garbage day in Kentucky,"), (2.6, 6.6, "and thanks to Mitch McConnell, things have gotten dirty."),
        (6.9, 9.5, "I'm Nate Morris, a Trump America First conservative,"), (9.5, 11.6, "and I'm here to take out the trash."),
        (11.8, 13.8, "So I know a little bit about garbage.")]

SKM, HAIRM = (238, 196, 170), (40, 30, 26)
VEST = (250, 120, 30)

bg = gradient((150, 200, 245), (230, 240, 250))
d0 = D(bg)
for x, c in ((60, (120, 80, 60)), (420, (150, 110, 80))):     # houses
    d0.p([(x, 300), (x + 150, 200), (x + 300, 300)], (90, 60, 50)); d0.r(x + 20, 300, x + 280, 470, c)
    d0.r(x + 120, 380, x + 180, 470, (70, 50, 40)); d0.r(x + 40, 330, x + 100, 380, (200, 230, 250), 0, (240, 240, 240), 4)
d0.r(0, 460, 1280, 720, (110, 170, 90)); d0.r(0, 560, 1280, 720, (90, 92, 98))
for x in range(0, 1280, 120): d0.r(x, 636, x + 60, 644, (230, 220, 120))


def truck(d, x):          # x = left edge of the rear hopper
    d.r(x, 210, x + 620, 560, (245, 245, 242), 18, (190, 190, 190), 4)
    d.r(x - 10, 260, x + 90, 520, (60, 64, 70), 10)                        # hopper mouth
    d.r(x - 30, 520, x + 110, 548, (200, 200, 200), 6)                     # step
    d.text(x + 380, 300, "DC SWAMP", 46, (200, 40, 50))
    d.text(x + 380, 360, "CLEANUP", 46, (200, 40, 50))
    for wx in (x + 180, x + 500):
        d.e(wx, 570, 58, 58, (30, 30, 34)); d.e(wx, 570, 24, 24, (160, 160, 160))


def mcconnell_cutout(d, x, y, ang=0.0, s=1.0):
    w, h = 90 * s, 200 * s
    dx = math.sin(ang) * 30
    d.r(x - w + dx, y - h, x + w + dx, y + h, (196, 160, 110), 6, (150, 116, 70), 4)
    d.p([(x - 70 * s + dx, y + h), (x + 70 * s + dx, y + h), (x + 60 * s + dx, y + 20 * s), (x - 60 * s + dx, y + 20 * s)], (40, 44, 60))
    hx, hy = x + dx, y - 70 * s
    d.e(hx, hy, 58 * s, 70 * s, (240, 214, 196))
    d.chord(hx, hy - 30 * s, 58 * s, 44 * s, 180, 360, (236, 236, 240))
    for sx in (-1, 1): d.e(hx + sx * 22 * s, hy - 6 * s, 16 * s, 14 * s, None, (60, 60, 60), 3 * s)
    d.a(hx, hy + 30 * s, 20 * s, 10 * s, 20, 160, (140, 70, 70), 4 * s)
    d.text(x + dx, y + 130 * s, "MITCH", 22 * s, (255, 255, 255))


def morris(d, hx, hy, mo, wink=False, arm=None, bag=None):
    by = hy + 96
    d.r(hx - 24, hy + 70, hx + 24, by + 10, SKM)
    d.p([(hx - 116, by), (hx + 116, by), (hx + 146, by + 330), (hx - 146, by + 330)], (34, 40, 70))
    d.p([(hx - 116, by), (hx - 30, by), (hx - 40, by + 330), (hx - 146, by + 330)], VEST)
    d.p([(hx + 116, by), (hx + 30, by), (hx + 40, by + 330), (hx + 146, by + 330)], VEST)
    for yy in (by + 120, by + 200):
        d.r(hx - 140, yy, hx - 36, yy + 18, (220, 220, 210)); d.r(hx + 36, yy, hx + 140, yy + 18, (220, 220, 210))
    puppet_head(d, hx, hy, 1.0, SKM, mo=mo, blink=False, look=(0.2, 0), rx=86, ry=98)
    if wink: d.e(hx + 34, hy - 14, 18, 16, SKM); d.a(hx + 34, hy - 16, 14, 8, 20, 160, (40, 25, 20), 4)
    d.chord(hx, hy - 44, 92, 70, 180, 360, HAIRM)
    d.e(hx - 30, hy - 100, 60, 30, HAIRM); d.e(hx + 34, hy - 96, 56, 28, HAIRM)
    for sx in (-1, 1): d.l([(hx + sx * 52, hy - 38), (hx + sx * 16, hy - 40)], HAIRM, 7)
    # arms
    lh = (hx - 160, by + 220)
    rh = arm or (hx + 160, by + 220)
    d.l([(hx - 110, by + 40), (hx - 150, by + 140), lh], VEST, 44)
    d.l([(hx + 110, by + 40), ((hx + 110 + rh[0]) / 2 + 20, (by + 40 + rh[1]) / 2 + 30), rh], VEST, 44)
    if bag: d.e(bag[0], bag[1], 46, 54, (30, 30, 34)); d.p([(bag[0] - 12, bag[1] - 54), (bag[0] + 12, bag[1] - 54), (bag[0], bag[1] - 74)], (30, 30, 34))
    for h in (lh, rh): d.e(h[0], h[1], 30, 28, (40, 40, 44))              # work gloves


def frame(t):
    img = bg.copy(); d = D(img)
    drive = ease((t - 16.2) / 1.4) * 1300
    tx = 760 + drive
    truck(d, tx)
    mo = mouth(t)
    MX, MY = 470, 250
    # Mitch cutout: stands by the curb, then flies into the hopper
    if t < T_TOSS + 0.6:
        if t < T_TOSS: cx, cy, ang = 250, 470, 0.0
        else:
            k = (t - T_TOSS) / 0.6
            cx, cy, ang = lerp(250, tx + 40, k), lerp(470, 380, k) - 260 * math.sin(math.pi * k), k * 6
        mcconnell_cutout(d, cx, cy, ang, 0.9)
    arm = None; bag = None
    if 2.7 < t < T_TOSS + 0.2: arm = (MX - 90, MY + 260)              # points at Mitch
    if 7.0 < t < T_BAG + 0.6:
        if t < T_BAG: bag = (MX + 175, MY + 250 - 60 * ease((t - 9.5) / 0.6)); arm = (MX + 170, bag[1] - 70)
        else:
            k = (t - T_BAG) / 0.6
            bag = (lerp(MX + 175, tx + 40, k), lerp(MY + 190, 380, k) - 160 * math.sin(math.pi * k)); arm = (MX + 190, MY + 140)
    # Morris, until the big hand takes him out with the trash
    if t < T_GRAB:
        morris(d, MX, MY - 4 * mo, mo, wink=13.4 < t < 14.0, arm=arm, bag=bag)
    elif t < T_DROP:
        k = ease((t - T_GRAB) / (T_DROP - T_GRAB))
        px = lerp(MX, tx + 40, k); py = lerp(MY, 200, math.sin(math.pi * min(1, k * 1.15))) if k < 0.85 else lerp(200, 360, (k - 0.85) / 0.15)
        morris(d, px, py, 0.6)
        d.text(px + 150, py - 80, "?!", 60, (255, 230, 80), stroke=5, sf=(40, 20, 20))
    if T_GRAB - 0.7 < t < T_DROP + 0.6:            # a familiar hand from above
        if t < T_GRAB: k = ease((t - T_GRAB + 0.7) / 0.7); hx_, hy_ = MX, lerp(-200, MY - 110, k)
        elif t < T_DROP:
            k = ease((t - T_GRAB) / (T_DROP - T_GRAB))
            hx_ = lerp(MX, tx + 40, k); hy_ = lerp(MY, 200, math.sin(math.pi * min(1, k * 1.15))) - 110 if k < 0.85 else lerp(90, 250, (k - 0.85) / 0.15)
        else: k = ease((t - T_DROP) / 0.6); hx_, hy_ = tx + 40, lerp(250, -260, k)
        d.r(hx_ - 46, hy_ - 400, hx_ + 46, hy_ - 60, SUIT)
        d.r(hx_ - 52, hy_ - 80, hx_ + 52, hy_ - 50, (250, 250, 250), 6)
        big_hand(d, hx_, hy_, 1.6)
    if t > 17.0:
        p = back((t - 17.0) / 0.4)
        if p > 0.02:
            w, h = 470 * p, 190 * p
            d.r(640 - w, 300 - h, 640 + w, 300 + h, (255, 250, 235), 24, (40, 60, 140), 8)
            d.text(640, 300 - 110 * p, "PLOT TWIST", 1 + 44 * p, (200, 40, 50))
            d.text(640, 300 - 20 * p, "Morris dropped out of the race.", 1 + 32 * p, (40, 40, 60), bold=False)
            d.text(640, 300 + 50 * p, "Next stop, courtesy of Trump:", 1 + 32 * p, (40, 40, 60), bold=False)
            d.text(640, 300 + 120 * p, "Ambassador to Colombia", 1 + 42 * p, (30, 80, 190))
    z, cx, cy = keyed(t, [(0, 1.12, 560, 380), (6.6, 1.12, 560, 380), (6.9, 1.2, 520, 340), (13.8, 1.2, 520, 340),
                          (14.2, 1.0, 640, 360)])
    return compose(img, z, cx, cy, t, CAPS)


if __name__ == "__main__":
    render("ky", frame, DUR, WAV, [1.5, 3.5, 4.8, 8.0, 10.4, 11.5, 13.6, 14.9, 15.4, 16.4, 17.6, 19.5])
