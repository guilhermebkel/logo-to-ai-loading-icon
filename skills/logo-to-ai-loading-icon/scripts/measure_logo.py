#!/usr/bin/env python3
"""Measure the parts of a logo SVG so you can animate them: bounding boxes, centers and a suggested viewBox.

For every <path>, <circle>, <rect>, <ellipse> and <g> it prints the box in the
element's LOCAL coordinate system (what you use when writing CSS inside the same
<g transform=...>) and in the file's viewBox space. With --split it separates each
subpath (M ... Z) of a <path>, which is useful when two letters, or a ring and its
hole, came in a single path.

Example:
  python measure_logo.py logo.svg --split
"""
import argparse
import json
import re
import sys
from pathlib import Path

JS = r"""
([split]) => {
  const svg = document.querySelector('svg');
  const m = svg.getScreenCTM().inverse();
  const pt = (x, y) => { const p = svg.createSVGPoint(); p.x = x; p.y = y; return p.matrixTransform(m); };
  const box = b => ({ x: +b.x.toFixed(2), y: +b.y.toFixed(2), w: +b.width.toFixed(2), h: +b.height.toFixed(2),
                      cx: +(b.x + b.width / 2).toFixed(2), cy: +(b.y + b.height / 2).toFixed(2) });
  const out = [];
  svg.querySelectorAll('path, circle, rect, ellipse, g').forEach((el, i) => {
    if (el.closest('defs, mask, clipPath')) return;
    let local; try { local = el.getBBox(); } catch (e) { return; }
    const r = el.getBoundingClientRect();
    const a = pt(r.left, r.top), b = pt(r.right, r.bottom);
    const item = { tag: el.tagName, id: el.id || null, class: el.getAttribute('class'),
                   transform: el.getAttribute('transform'), local: box(local),
                   in_viewBox: { x: +a.x.toFixed(2), y: +a.y.toFixed(2), w: +(b.x - a.x).toFixed(2), h: +(b.y - a.y).toFixed(2) } };
    if (split && el.tagName === 'path') {
      const parts = (el.getAttribute('d').match(/[Mm][^Mm]*/g) || []);
      if (parts.length > 1) {
        item.subpaths = parts.map((d, k) => {
          const t = document.createElementNS('http://www.w3.org/2000/svg', 'path');
          t.setAttribute('d', d); el.parentNode.appendChild(t);
          const bb = t.getBBox(); el.parentNode.removeChild(t);
          return { index: k, ...box(bb), d_start: d.slice(0, 40) };
        });
      }
    }
    out.push(item);
  });
  return { viewBox: svg.getAttribute('viewBox'), items: out };
}
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("svg")
    ap.add_argument("--split", action="store_true", help="measure each subpath of a <path>")
    ap.add_argument("--margin", type=float, default=0.12, help="margin when suggesting a viewBox (fraction of the longest side)")
    args = ap.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Playwright is not installed (pip install playwright && playwright install chromium).")

    svg = Path(args.svg).read_text(encoding="utf-8")
    svg = re.sub(r"<svg\b", '<svg width="800" height="800"', svg, count=1)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 800, "height": 800})
        page.set_content(f"<html><body style='margin:0'>{svg}</body></html>")
        res = page.evaluate(JS, [args.split])
        browser.close()

    print(json.dumps(res, ensure_ascii=False, indent=2))

    # suggested viewBox from paths/circles (ignores <g> and a background that fills everything)
    boxes = [i["in_viewBox"] for i in res["items"] if i["tag"] in ("path", "circle", "ellipse")]
    if boxes:
        x0 = min(c["x"] for c in boxes); y0 = min(c["y"] for c in boxes)
        x1 = max(c["x"] + c["w"] for c in boxes); y1 = max(c["y"] + c["h"] for c in boxes)
        m = max(x1 - x0, y1 - y0) * args.margin
        print(f"\ncontent in the file's viewBox: x {x0:.1f}..{x1:.1f}, y {y0:.1f}..{y1:.1f}")
        print(f"suggested viewBox (margin {args.margin:.0%}): {x0 - m:.1f} {y0 - m:.1f} {x1 - x0 + 2 * m:.1f} {y1 - y0 + 2 * m:.1f}")
        print("tip: to animate only the shapes without a background tile, work in the LOCAL coordinates of the <g> and use a viewBox around them.")


if __name__ == "__main__":
    main()
