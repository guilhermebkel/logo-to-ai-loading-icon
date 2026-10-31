#!/usr/bin/env python3
"""Render frames of an animated SVG (CSS or SMIL) at fixed points of the cycle.

Uses Chromium through Playwright: it pauses every animation, sets the clock to
fraction x duration and takes a screenshot. Use it to check the choreography
without watching the loop in real time.

Examples:
  python render_frames.py loader.svg --duration 6 --sheet sheet.png
  python render_frames.py loader.svg --duration 6 --fractions 0,0.25,0.5,0.75 --out frames
  python render_frames.py loader.svg --duration 6 --sizes 16,24,32,48 --sheet small.png
"""
import argparse
import re
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("svg")
    ap.add_argument("--duration", type=float, required=True, help="cycle duration in seconds")
    ap.add_argument("--fractions", default="0.02,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,0.98",
                    help="comma-separated fractions of the cycle (0 to 1)")
    ap.add_argument("--out", default="frames", help="folder for the PNG files")
    ap.add_argument("--width", type=int, default=240)
    ap.add_argument("--height", type=int, default=220)
    ap.add_argument("--background", default="#ffffff", help="page background color, or 'transparent'")
    ap.add_argument("--sheet", help="if given, also build a contact sheet PNG at this path")
    ap.add_argument("--columns", type=int, default=6)
    ap.add_argument("--sizes", help="comma-separated pixel sizes (e.g. 16,24,32,48): render ONE frame "
                                    "(--fractions, first value) at each size to check small-size legibility")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Playwright is not installed (pip install playwright && playwright install chromium).")

    fractions = [float(x) for x in args.fractions.split(",") if x.strip()]
    svg = Path(args.svg).read_text(encoding="utf-8")
    bg = "transparent" if args.background == "transparent" else args.background

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # each job = (label, fraction, width, height)
    if args.sizes:
        sizes = [int(s) for s in args.sizes.split(",") if s.strip()]
        jobs = [(f"{s}px", fractions[0], s, s) for s in sizes]
        cell_w = cell_h = max(sizes) + 24
    else:
        jobs = [(f"{f * 100:.0f}%", f, args.width, args.height) for f in fractions]
        cell_w, cell_h = args.width, args.height

    files = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": cell_w, "height": cell_h})
        for i, (label, f, w, h) in enumerate(jobs):
            sized = re.sub(r"<svg\b", f'<svg width="{w}" height="{h}"', svg, count=1)
            html = (f"<html><body style='margin:0;background:{bg};display:grid;place-items:center;"
                    f"width:{cell_w}px;height:{cell_h}px'>{sized}</body></html>")
            page.set_content(html)
            page.wait_for_timeout(150)
            t = f * args.duration
            page.evaluate(
                """([ms, s]) => {
                    document.getAnimations().forEach(a => { a.pause(); a.currentTime = ms; });
                    const el = document.querySelector('svg');
                    if (el && el.pauseAnimations) { el.pauseAnimations(); el.setCurrentTime(s); }
                }""",
                [t * 1000, t],
            )
            path = out / f"frame_{i:02d}.png"
            page.screenshot(path=str(path), omit_background=(bg == "transparent"))
            files.append((path, label))
        browser.close()
    print(f"{len(files)} frames in {out}/")

    if args.sheet:
        from PIL import Image, ImageDraw
        ims = [Image.open(p).convert("RGB") for p, _ in files]
        w, h = ims[0].size
        cols = min(args.columns, len(ims))
        rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w, rows * h), (255, 255, 255))
        d = ImageDraw.Draw(sheet)
        for i, (im, (_, label)) in enumerate(zip(ims, files)):
            x, y = (i % cols) * w, (i // cols) * h
            sheet.paste(im, (x, y))
            d.rectangle([x, y, x + w - 1, y + h - 1], outline=(215, 215, 215))
            d.text((x + 4, y + 4), label, fill=(120, 120, 120))
        sheet.save(args.sheet)
        print("contact sheet:", args.sheet, sheet.size)


if __name__ == "__main__":
    main()
