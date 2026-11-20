#!/usr/bin/env python3
"""Render the news-image-20261120 front page (1024x1024 PNG) with Pillow.

Draws a classic newspaper front page summarising Friday 20 November 2026:
lead story (Trump defers the Iran decision to 2027), Cyclone Akvan,
Voyager 1's light-day milestone, plus a three-item bottom strip. All artwork
is flat shapes and text drawn by this program; no external images.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

W, H = 1024, 1024
PAPER = (247, 243, 233)   # warm off-white
INK = (26, 26, 26)        # near-black
RED = (138, 31, 31)       # dark-red accent
GREY = (90, 86, 76)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

M = 56                      # margin
CW = W - 2 * M              # content width = 912


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_centered(draw, cx, y, lines, fnt, fill=INK, leading=None):
    """Draw lines centred on cx; returns y below the last line."""
    lh = leading or int(fnt.size * 1.18)
    for line in lines:
        w = draw.textlength(line, font=fnt)
        draw.text((cx - w / 2, y), line, font=fnt, fill=fill)
        y += lh
    return y


def draw_block(draw, x, y, lines, fnt, fill=INK, leading=None):
    """Draw left-aligned lines; returns y below the last line."""
    lh = leading or int(fnt.size * 1.28)
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += lh
    return y


def rule(draw, y, x0=M, x1=W - M, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    rule(d, 34, width=3)
    y = 52
    y = draw_centered(d, W // 2, y,
                      ["THE WORLD IN ONE PICTURE"],
                      font(SERIF_B, 56), leading=64)
    y += 6
    y = draw_centered(d, W // 2, y,
                      ["FRIDAY  ·  20 NOVEMBER 2026"],
                      font(SANS_B, 24), leading=30)
    y += 12
    rule(d, y, width=2)
    rule(d, y + 5, width=1)
    y += 22

    # ---- Lead story -----------------------------------------------------
    lead_head = font(SERIF_B, 47)
    head_lines = wrap(d, "TRUMP PUTS IRAN WAR DECISION OFF UNTIL 2027",
                      lead_head, CW)
    y = draw_centered(d, W // 2, y, head_lines, lead_head, leading=56)
    y += 8
    sub = font(SERIF, 21)
    sub_lines = wrap(
        d,
        "The president says there is \u201cno rush\u201d and he will \u201csee what "
        "happens\u201d after 1 January, pushing any decision into next year.",
        sub, CW)
    y = draw_centered(d, W // 2, y, sub_lines, sub, fill=GREY, leading=27)
    y += 18

    # ---- Lead graphic: 2027 calendar + clock ---------------------------
    gy0 = y
    gy1 = y + 176
    # Calendar card (left).
    cal_x0, cal_x1 = 96, 500
    d.rectangle([cal_x0, gy0, cal_x1, gy1], fill=(255, 255, 255),
                outline=INK, width=3)
    d.rectangle([cal_x0, gy0, cal_x1, gy0 + 44], fill=RED)
    y2027 = font(SERIF_B, 30)
    t = "2027"
    d.text((cal_x0 + (cal_x1 - cal_x0 - d.textlength(t, font=y2027)) / 2,
            gy0 + 6), t, font=y2027, fill=(255, 255, 255))
    # Month grid: 7 columns x 3 rows of day squares; 1 January circled.
    # Cells are 32 px so the whole grid fits inside the card above the label.
    cell = 32
    gx, gy = cal_x0 + 34, gy0 + 54
    for r in range(3):
        for c in range(7):
            x0, y0 = gx + c * cell, gy + r * cell
            d.rectangle([x0, y0, x0 + 30, y0 + 30], outline=GREY, width=1)
    d.ellipse([gx - 5, gy - 5, gx + 37, gy + 37], outline=RED, width=4)
    one = font(SANS_B, 19)
    d.text((gx + 10, gy + 5), "1", font=one, fill=RED)
    jan = font(SANS_B, 15)
    label = "JANUARY  ·  DECISION DUE AFTER 1 JAN"
    d.text((cal_x0 + (cal_x1 - cal_x0 - d.textlength(label, font=jan)) / 2,
            gy1 - 20), label, font=jan, fill=INK)
    # Arrow from calendar to clock.
    ax0, ax1, ay = cal_x1 + 18, 636, gy0 + 84
    d.line([(ax0, ay), (ax1, ay)], fill=RED, width=5)
    d.polygon([(ax1, ay), (ax1 - 18, ay - 11), (ax1 - 18, ay + 11)], fill=RED)
    # Clock (right): 10:10, captioned "NO RUSH".
    cx, cy, r = 776, gy0 + 84, 76
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255),
              outline=INK, width=4)
    for i in range(12):
        a = math.radians(i * 30 - 90)
        x0 = cx + (r - 8) * math.cos(a)
        y0 = cy + (r - 8) * math.sin(a)
        x1 = cx + (r - 18) * math.cos(a)
        y1 = cy + (r - 18) * math.sin(a)
        d.line([(x0, y0), (x1, y1)], fill=INK, width=3)
    # Hour hand to 10, minute hand to 2 (10:10).
    ha = math.radians(10 * 30 - 90)
    d.line([(cx, cy), (cx + 40 * math.cos(ha), cy + 40 * math.sin(ha))],
           fill=INK, width=6)
    ma = math.radians(2 * 30 - 90)
    d.line([(cx, cy), (cx + 58 * math.cos(ma), cy + 58 * math.sin(ma))],
           fill=INK, width=4)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED)
    cap = font(SANS_B, 20)
    ct = "NO RUSH"
    d.text((cx - d.textlength(ct, font=cap) / 2, cy + r + 10), ct,
           font=cap, fill=RED)

    y = gy1 + 20
    rule(d, y, width=2)
    y += 18

    # ---- Two columns ----------------------------------------------------
    col_w = (CW - 40) // 2
    col_y = y
    cols = [
        ("CYCLONE AKVAN BEARS DOWN ON ODISHA",
         "About 300,000 people have been evacuated and 423 rescue teams "
         "deployed as the severe cyclone heads for India's east coast, with "
         "landfall expected today."),
        ("VOYAGER 1, A LIGHT-DAY FROM HOME",
         "NASA confirms the probe, launched in 1977, is now so far away "
         "that a radio signal takes a full 24 hours to reach it \u2014 a "
         "first for any spacecraft."),
    ]
    col_bottom = col_y
    for i, (head, body) in enumerate(cols):
        x = M + i * (col_w + 40)
        hf = font(SERIF_B, 27)
        hl = wrap(d, head, hf, col_w)
        yy = draw_block(d, x, col_y, hl, hf, leading=33)
        yy += 6
        bf = font(SANS, 18)
        bl = wrap(d, body, bf, col_w)
        yy = draw_block(d, x, yy, bl, bf, fill=(40, 40, 40), leading=24)
        col_bottom = max(col_bottom, yy)
    # Vertical divider between columns.
    d.line([(W // 2, col_y), (W // 2, col_bottom)], fill=GREY, width=1)

    y = col_bottom + 16
    rule(d, y, width=2)
    y += 16

    # ---- Bottom strip: three short items -------------------------------
    strip_w = (CW - 2 * 28) // 3
    items = [
        ("SUMMIT IN CHINA",
         "Trump, Xi and Putin hold first three-way meeting",
         "Nuclear risks and energy security on the agenda at the APEC "
         "gathering in Shenzhen."),
        ("UN COURT",
         "Myanmar committed genocide, judges rule",
         "The top UN court finds the military intended to destroy a "
         "substantial part of the Rohingya."),
        ("CULTURE",
         "GTA 6 sales pass $1.8 billion",
         "Rockstar's blockbuster has already out-earned the global run of "
         "The Odyssey."),
    ]
    strip_bottom = y
    for i, (kick, head, body) in enumerate(items):
        x = M + i * (strip_w + 28)
        kf = font(SANS_B, 15)
        d.text((x, y), kick, font=kf, fill=RED)
        yy = y + 22
        hf = font(SERIF_B, 20)
        hl = wrap(d, head, hf, strip_w)
        yy = draw_block(d, x, yy, hl, hf, leading=25)
        yy += 4
        bf = font(SANS, 15)
        bl = wrap(d, body, bf, strip_w)
        yy = draw_block(d, x, yy, bl, bf, fill=(40, 40, 40), leading=20)
        strip_bottom = max(strip_bottom, yy)
        if i < 2:
            vx = x + strip_w + 14
            d.line([(vx, y), (vx, strip_bottom)], fill=GREY, width=1)

    y = strip_bottom + 14
    rule(d, y, width=2)
    y += 12
    foot = font(SANS_B, 15)
    ft = "ALL THE NEWS OF FRIDAY 20 NOVEMBER 2026  ·  IN ONE PICTURE"
    d.text(((W - d.textlength(ft, font=foot)) / 2, y), ft, font=foot, fill=INK)

    img.save(OUT, "PNG", optimize=True)
    print(f"wrote {OUT} {W}x{H}")


if __name__ == "__main__":
    main()
