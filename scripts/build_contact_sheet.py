#!/usr/bin/env python3
"""Lay storyboard keyframes into a single labeled contact sheet for approval.

Usage:
    python build_contact_sheet.py \
        --frames f1.png f2.png f3.png f4.png \
        --labels "1 · 2s · CU product" "2 · 4s · woman uses it" \
                 "3 · 4s · lifestyle wide" "4 · 3s · product hero" \
        --out storyboard.png --cols 3 --title "ACME — 15s spot"

Requires Pillow:  pip install pillow --break-system-packages
"""
import argparse
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required: pip install pillow --break-system-packages")


def _font(size):
    for p in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--frames", nargs="+", required=True, help="Keyframe image paths, in order.")
    ap.add_argument("--labels", nargs="*", default=[], help="Caption per frame (same order).")
    ap.add_argument("--out", default="storyboard.png")
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--cell", type=int, default=480, help="Cell width in px (default 480).")
    ap.add_argument("--title", default="Storyboard")
    args = ap.parse_args()

    frames = args.frames
    labels = args.labels + [""] * (len(frames) - len(args.labels))
    cols = max(1, args.cols)
    rows = (len(frames) + cols - 1) // cols

    cw = args.cell
    pad = 16
    cap_h = 40
    title_h = 64

    # Use first image aspect to size cells.
    with Image.open(frames[0]) as im0:
        ar = im0.height / im0.width
    ch = int(cw * ar)
    cell_total_h = ch + cap_h

    W = cols * cw + (cols + 1) * pad
    H = title_h + rows * cell_total_h + (rows + 1) * pad

    sheet = Image.new("RGB", (W, H), (18, 18, 20))
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, pad), args.title, fill=(255, 255, 255), font=_font(34))

    tf = _font(20)
    for i, fpath in enumerate(frames):
        r, c = divmod(i, cols)
        x = pad + c * (cw + pad)
        y = title_h + pad + r * (cell_total_h + pad)
        try:
            with Image.open(fpath) as im:
                im = im.convert("RGB")
                im.thumbnail((cw, ch))
                ox = x + (cw - im.width) // 2
                oy = y + (ch - im.height) // 2
                sheet.paste(im, (ox, oy))
        except Exception as e:  # noqa
            draw.rectangle([x, y, x + cw, y + ch], outline=(120, 120, 120))
            draw.text((x + 8, y + 8), f"missing: {fpath}\n{e}", fill=(220, 80, 80), font=tf)
        draw.text((x + 4, y + ch + 8), labels[i], fill=(230, 230, 230), font=tf)

    sheet.save(args.out)
    print(args.out)


if __name__ == "__main__":
    main()
