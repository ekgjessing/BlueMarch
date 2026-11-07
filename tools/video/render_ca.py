"""California: "Just Try It, California." (Steve Hilton for Governor ad, posted on X Oct 1 2026).

Audio: https://x.com/SteveHiltonx/status/2105770019921809537 (kept locally in lyd/ca-just-try-it.mp4).
The two women in the ad are actors, so their puppets are generic. Hilton gets the cameo.
"""
import math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from puppet import *

SRC = os.path.join(ROOT, "lyd", "ca-just-try-it.mp4")
DUR = 25.5
TMP = os.path.join(ROOT, "video")

# (src_start, src_end, video_start)
SEGS = [(2.5, 13.3, 0.3), (14.3, 18.4, 11.3), (21.3, 23.9, 15.9), (38.3, 40.9, 18.9), (44.6, 45.9, 22.0)]
def v(src):
    for a, b, t0 in SEGS:
        if a <= src <= b: return src - a + t0
    raise ValueError(src)

mix = Mix(DUR)
for a, b, t0 in SEGS: mix.add(fade(load(SRC, a, b), 0.08, 0.15), t0)
mix.add(sfx_snip(0.35), v(23.6) - 0.2)                         # pen tick
lick = np.random.default_rng(3).uniform(-1, 1, int(0.5 * SR)).astype(np.float32)
lick *= np.sin(np.linspace(0, math.pi, len(lick))) ** 2 * 0.18
mix.add(lick, 23.25)
for k, s in enumerate(sfx_chime(0.2)): mix.add(s, 24.35 + k * 0.11)
WAV = os.path.join(TMP, "ca_audio.wav"); mix.write(WAV)

B_WORDS = [(2.78, 4.48), (8.36, 9.52), (9.52, 10.56), (10.74, 11.82), (38.5, 39.52), (39.52, 40.7)]   # blue hair
R_WORDS = [(5.24, 6.04), (6.78, 7.68), (11.92, 13.0), (14.52, 15.66), (17.0, 18.1), (21.56, 23.7), (44.78, 45.66)]
def spans(ws):
    out = []
    for a, b in ws:   # split long phrases into ~0.22 s syllables
        n = max(1, int((b - a) / 0.22))
        for i in range(n): out.append((v(a) + (b - a) * i / n, v(a) + (b - a) * (i + 1) / n))
    return out
mB, mR = Mouth(spans(B_WORDS)), Mouth(spans(R_WORDS))

CAPS = [(0.4, 2.6, "I can't believe I'm doing this."), (2.9, 5.7, "Don't be nervous. It's not that bad."),
        (6.0, 8.1, "I've just never done anything like this before."), (8.1, 9.7, "Like, what if my dad finds out?"),
        (9.7, 11.0, "Just try it."), (11.4, 13.4, "Look, give me your hand."), (13.8, 15.5, "Close your eyes…"),
        (15.9, 18.6, "…and I'll do all the work."), (18.9, 21.6, "I think… I think I liked it."), (22.0, 23.4, "Now lick it.")]

BX, RX, HY = 430, 850, 300
SKB, SKR, SKH = (242, 210, 188), (236, 196, 168), (236, 188, 156)
HB, HR = (46, 80, 210), (214, 52, 72)

bg = gradient((40, 26, 26), (14, 10, 12))
d0 = D(bg)
cols = [(200, 60, 60), (220, 130, 50), (220, 200, 70), (70, 150, 80), (60, 90, 190), (130, 70, 160)]
for i, c in enumerate(cols):          # chevron wall hanging
    y = 40 + i * 34
    d0.p([(300, y), (640, y + 150), (980, y), (980, y + 34), (640, y + 184), (300, y + 34)], shade(c, 0.55))
d0.r(0, 520, 1280, 720, (70, 50, 60)); d0.r(0, 500, 1280, 540, (110, 84, 92), 20)   # bed
d0.e(120, 210, 40, 40, (255, 220, 150))
bg = glow(bg, [(120, 210, 260, 260, (255, 200, 120, 110)), (640, 360, 500, 260, (255, 170, 120, 40))])


def girl(d, hx, hy, skin, hair, mo, eyes_closed=False, look=(0, 0), smile=False, shirt=(80, 80, 84), word=None, tongue=0.0):
    d.e(hx, hy + 70, 120, 190, hair)                                         # long hair behind
    d.p([(hx - 120, 520), (hx + 120, 520), (hx + 150, 720), (hx - 150, 720)], shirt)
    d.r(hx - 22, hy + 70, hx + 22, 520, skin)
    d.p([(hx - 125, hy + 175), (hx + 125, hy + 175), (hx + 150, 720), (hx - 150, 720)], shirt)
    if word: d.text(hx, 600, word, 40, (230, 230, 230))
    puppet_head(d, hx, hy, 0.95, skin, mo=mo, look=look, blink=eyes_closed, rx=84, ry=96)
    for sx in (-1, 1):
        ex = hx + sx * 32
        if not eyes_closed:
            for k in range(3): d.l([(ex + sx * (6 + k * 5), hy - 25), (ex + sx * (10 + k * 7), hy - 36)], (30, 20, 20), 2.5)
    if smile and mo < 0.08:
        d.a(hx, hy + 40, 26, 16, 20, 160, (150, 50, 60), 5)
    if tongue > 0:
        d.e(hx, hy + 62 + 22 * tongue, 18, 10 + 26 * tongue, (236, 100, 120), (180, 60, 80), 3)
    d.chord(hx, hy - 34, 92, 76, 180, 360, hair)                             # fringe
    d.p([(hx - 92, hy - 34), (hx - 40, hy - 34), (hx - 70, hy + 20)], hair)
    d.p([(hx + 92, hy - 34), (hx + 40, hy - 34), (hx + 70, hy + 20)], hair)


def hilton(d, hx, hy, mo=0.0):
    d.p([(hx - 110, hy + 110), (hx + 110, hy + 110), (hx + 140, hy + 400), (hx - 140, hy + 400)], (24, 24, 28))
    d.r(hx - 22, hy + 80, hx + 22, hy + 120, SKH)
    puppet_head(d, hx, hy, 0.9, SKH, mo=mo, look=(0, -0.3), rx=86, ry=100, teeth=mo < 0.08)
    d.a(hx, hy - 10, 86 * 0.9, 100 * 0.9, 200, 340, shade(SKH, 1.08), 6)    # shiny dome
    d.e(hx - 30, hy - 70, 14, 8, (255, 240, 225))
    for sx in (-1, 1): d.l([(hx + sx * 50, hy - 36), (hx + sx * 16, hy - 40)], (110, 90, 80), 6)


def ballot(d, x, y, filled):
    d.r(x - 130, y - 80, x + 130, y + 80, (250, 250, 242), 6, (160, 160, 160), 3)
    d.text(x, y - 58, "BALLOT", 22, (40, 40, 60))
    for i, name in enumerate(["HILTON", "THE OTHER GUY"]):
        yy = y - 16 + i * 44
        d.e(x - 96, yy, 13, 13, (40, 40, 40) if (i == 0 and filled) else None, (60, 60, 60), 3)
        d.text(x - 72, yy, name, 18, (60, 60, 70), anchor="lm", bold=False)


def envelope(d, x, y, closed):
    d.r(x - 120, y - 70, x + 120, y + 70, (248, 246, 236), 6, (170, 170, 170), 3)
    for k in range(12):
        c = (200, 40, 50) if k % 2 else (40, 80, 190)
        d.r(x - 120 + k * 20, y + 58, x - 104 + k * 20, y + 70, c)
    if closed: d.p([(x - 120, y - 70), (x + 120, y - 70), (x, y + 10)], (230, 226, 214), (170, 170, 170), 3)
    else: d.p([(x - 120, y - 70), (x + 120, y - 70), (x, y - 150)], (230, 226, 214), (170, 170, 170), 3)


def frame(t):
    img = bg.copy(); d = D(img)
    closed = 14.0 <= t < 18.6
    tongue = clamp(math.sin(math.pi * (t - 23.2) / 0.8)) if 23.2 <= t < 24.0 else 0.0
    girl(d, BX, HY + (4 if mB(t) else 0), SKB, HB, mB(t), eyes_closed=closed, look=(1, 0) if t < 18.6 else (0.4, 0),
         smile=t > 20.6, word="RESIST")
    girl(d, RX, HY, SKR, HR, mR(t), look=(-1, 0), smile=mR(t) == 0 and t > 9.7, shirt=(120, 70, 50))
    # Hilton pops up in front of the bed for "I'll do all the work"
    hp = back((t - 15.5) / 0.45) if t >= 15.5 else 0.0
    hy_h = lerp(1000, 360, hp)
    if t >= 15.5: hilton(d, 640, hy_h)
    # hands: R takes B's hand, then both rest on the ballot's right edge
    g = ease((t - 11.6) / 0.6)
    bh = (lerp(520, 610, g), lerp(600, 540, g)); rh = (lerp(760, 670, g), lerp(600, 540, g))
    if t > 15.6:
        k = ease((t - 15.6) / 0.6); bh = (lerp(bh[0], 790, k), lerp(bh[1], 600, k)); rh = (lerp(rh[0], 790, k), lerp(rh[1], 520, k))
    if 15.5 <= t < 21.8:
        drop = ease((t - 21.3) / 0.5) * 300
        bx, by = 640, hy_h + 175 + drop
        ballot(d, bx, by, t > 17.6)
        if t > 16.6:     # Hilton's pen does all the work
            px, py = bx - 96 + 8 * math.sin(t * 28) * (1 if t < 17.6 else 0), by - 16
            d.l([(px, py), (px - 40, py + 90)], (30, 30, 40), 10); d.p([(px - 5, py - 2), (px + 5, py - 2), (px, py - 12)], (240, 200, 60))
            hand(d, px - 44, py + 96, 0.8, SKH)
    env = None
    if t >= 21.7:
        if t < 24.2: ex, ey = lerp(1000, BX + 90, ease((t - 21.8) / 0.5)), 500
        else: ex, ey = lerp(BX + 90, 640, ease((t - 24.2) / 0.4)), lerp(500, 540, ease((t - 24.2) / 0.4))
        envelope(d, ex, ey, t > 23.9); env = (ex, ey)
        rh = (ex + 100, ey + 40); bh = (ex - 100, ey + 40) if t > 24.2 else bh
    if tongue > 0:
        hx, hy = BX, HY
        d.e(hx, hy + 62 + 22 * tongue, 18, 10 + 26 * tongue, (236, 100, 120), (180, 60, 80), 3)
    d.l([(BX + 100, 560), ((BX + 100 + bh[0]) / 2, max(600, bh[1] + 30)), bh], SKB, 30)
    d.l([(RX - 100, 560), ((RX - 100 + rh[0]) / 2, max(600, rh[1] + 30)), rh], SKR, 30)
    hand(d, *bh, 0.8, SKB); hand(d, *rh, 0.8, SKR)
    if env and t > 24.2:
        p = back((t - 24.2) / 0.3)
        d.r(640 - 160 * p, 110 - 34 * p, 640 + 160 * p, 110 + 34 * p, (40, 110, 230), 10, (255, 255, 255), 4)
        if p > 0.3: d.text(640, 110, "MAIL-IN BALLOT", int(28 * p), (255, 255, 255))
    if 9.7 <= t < 11.0:
        p = back((t - 9.75) / 0.3)
        d.text(1090, 150, "!", 1 + 110 * p, (255, 230, 120), stroke=5, sf=(40, 20, 20))
    cx, z = keyed(t, CAM)
    return compose(img, z, cx, 330, t, CAPS)


L, R_ = BX + 70, RX - 70
CAM = [(0, L, 1.18), (2.6, L, 1.18), (3.0, R_, 1.18), (5.7, R_, 1.18), (6.0, L, 1.18), (9.5, L, 1.18), (9.8, R_, 1.18),
       (13.6, R_, 1.12), (14.0, 640, 1.1), (15.3, 640, 1.1), (15.6, 640, 1.0), (18.7, 640, 1.0), (19.0, L, 1.22),
       (21.5, L, 1.22), (21.9, 640, 1.0)]


if __name__ == "__main__":
    render("ca", frame, DUR, WAV, [1.2, 4.0, 8.5, 12.4, 14.6, 16.4, 18.0, 20.0, 22.6, 23.5, 24.8, 25.3])
