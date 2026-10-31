# Verification

You cannot watch the loop in real time, so check it frame by frame.

## Routine

1. `python scripts/validate_svg.py file.svg`: fix every ERROR and WARN.
2. `python scripts/render_frames.py file.svg --duration <s> --sheet sheet.png`. Default fractions are 2%, 10% … 98%. Use `--fractions` to zoom in on a suspicious stretch (for example `0,0.01,0.02`).
3. Open `sheet.png` and look at it. Check:
   - **Rest:** are the first and last frames identical?
   - **Contact:** do pieces touch or merge in any frame?
   - **Cuts:** does a shape vanish or jump between neighboring frames for no reason?
   - **Artifacts:** stray dots, hairlines, strokes ahead of the head.
   - **Framing:** nothing clipped by the viewBox at the farthest point of the orbit.
4. Small sizes: `python scripts/render_frames.py file.svg --duration <s> --fractions 0.3 --sizes 16,24,32,48 --sheet small.png`. If the shapes become unreadable dots below your target size, change recipe or use `--fit`.
5. Dark background: render with `--background "#16181d"` and a light `--color`.
6. If the destination needs a fallback: `python scripts/export_fallback.py file.svg --duration <s> --format webp --out loader.webp` and check the size (lossy WebP with `--quality 85` stays in the tens of KB).

## Limits

- `render_frames.py` uses Chromium. The six built-in recipes were also compared in Firefox and WebKit (Playwright's WebKit build, the engine behind Safari) at two points of each cycle, with at most a handful of differing pixels at 200 px. Hand-written SVG can still differ, especially with animated `clipPath` or `transform-box`; tell the user if the target is Safari and you did not test it.
- The contact sheet shows poses, not rhythm. Check rhythm by reading the durations and the `animation-timing-function` values.
- `render_frames.py` sets the animation clock directly. Do not use a "freeze with a single negative `animation-delay`" harness: it breaks elements that have several animations with different delays (the fill appears too early).
