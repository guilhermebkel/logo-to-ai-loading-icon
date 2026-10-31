#!/usr/bin/env python3
"""Export an animated SVG (CSS) as an animated WebP or GIF, for places that cannot show animated SVG.

Renders the whole cycle frame by frame in Chromium and assembles the file with Pillow.
WebP keeps real transparency; GIF only has 1-bit transparency (jagged edges on a
background different from the expected one), so prefer WebP or use --background
to get a GIF with a solid background.

Example:
  python export_fallback.py loader.svg --duration 6 --fps 24 --size 160 --format webp --out loader.webp
"""
import argparse
import io
import re
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("svg")
    ap.add_argument("--duration", type=float, required=True, help="cycle duration in seconds")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--size", type=int, default=160, help="longest side, in pixels")
    ap.add_argument("--format", choices=["webp", "gif"], default="webp")
    ap.add_argument("--background", default="transparent", help="solid color (e.g. #ffffff) or 'transparent'")
    ap.add_argument("--quality", type=int, default=85,
                    help="WebP: 1 to 99 uses lossy compression (smaller file); 100 uses lossless (larger)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    try:
        from playwright.sync_api import sync_playwright
        from PIL import Image
    except ImportError:
        sys.exit("Needs Playwright (with Chromium) and Pillow.")

    svg = Path(a.svg).read_text(encoding="utf-8")
    m = re.search(r'viewBox="([-\d.\s,]+)"', svg)
    vb = [float(v) for v in re.split(r"[\s,]+", m.group(1).strip())] if m else [0, 0, 100, 100]
    ratio = vb[2] / vb[3]
    w, h = (a.size, round(a.size / ratio)) if ratio >= 1 else (round(a.size * ratio), a.size)
    svg = re.sub(r"<svg\b", f'<svg width="{w}" height="{h}"', svg, count=1)
    transparent = a.background == "transparent"
    html = f"<html><body style='margin:0;background:{'transparent' if transparent else a.background}'>{svg}</body></html>"

    n = max(2, round(a.duration * a.fps))
    frames = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": w, "height": h})
        page.set_content(html)
        page.wait_for_timeout(200)
        for i in range(n):
            t = a.duration * i / n
            page.evaluate(
                """([ms, s]) => {
                    document.getAnimations().forEach(x => { x.pause(); x.currentTime = ms; });
                    const el = document.querySelector('svg');
                    if (el && el.pauseAnimations) { el.pauseAnimations(); el.setCurrentTime(s); }
                }""",
                [t * 1000, t],
            )
            png = page.screenshot(omit_background=transparent)
            frames.append(Image.open(io.BytesIO(png)).convert("RGBA"))
        browser.close()

    frame_ms = round(1000 / a.fps)
    if a.format == "webp":
        if a.quality >= 100:
            frames[0].save(a.out, save_all=True, append_images=frames[1:], duration=frame_ms, loop=0,
                           lossless=True, exact=True)
        else:
            frames[0].save(a.out, save_all=True, append_images=frames[1:], duration=frame_ms, loop=0,
                           lossless=False, quality=a.quality, alpha_quality=a.quality, method=6)
    else:
        if transparent:
            pal = []
            for fr in frames:
                p8 = fr.convert("RGB").convert("P", palette=Image.ADAPTIVE, colors=255)
                mask = fr.split()[3].point(lambda v: 255 if v < 128 else 0)
                p8.paste(255, mask)
                pal.append(p8)
            pal[0].save(a.out, save_all=True, append_images=pal[1:], duration=frame_ms, loop=0,
                        disposal=2, transparency=255)
        else:
            rgb = [fr.convert("RGB") for fr in frames]
            rgb[0].save(a.out, save_all=True, append_images=rgb[1:], duration=frame_ms, loop=0, disposal=2)
    size_kb = Path(a.out).stat().st_size / 1024
    print(f"ok {a.out}: {n} frames, {w}x{h}, {size_kb:.1f} KB")


if __name__ == "__main__":
    main()
