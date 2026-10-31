#!/usr/bin/env python3
"""Generate AI-loading icons as SVG (pure CSS) from a ring and a cross taken from a logo.

The ring comes from a round letter or dot with a hole (an "o") and the cross comes
from a letter with a crossbar (a "t"). The default proportions (hole = 42.3% of the
outer radius) are a reasonable starting point; replace them with the numbers of your
brand using --hole-ratio, --ring-radius, --arm and --thickness (get them with
measure_logo.py).

Recipes (all start and end in the resting row: ring, cross, ring):
  orbit       row -> triangle -> one full turn (cross spinning) -> row
  swap        the three pieces trade places along arcs, over and under each other
  satellites  two rings circle the cross in an ellipse while the cross spins in place
  breathe     like "orbit", but the triangle opens and closes while it turns
  bloom       a central ring sends out smaller pieces (rings and crosses) that return
  hop         ring, cross and ring hop in a wave; the cross turns 90 degrees per hop

Examples:
  python generate_symbols.py --recipe bloom --out bloom.svg --color "#3B5BDB"
  python generate_symbols.py --recipe hop --out hop-dark.svg --color "#F5F5F5"
  python generate_symbols.py --list

After generating, ALWAYS check the result with render_frames.py: overlapping pieces
and pieces leaving the viewBox only show up when you look at the frames.
"""
import argparse
import math
import re
import sys

CFG = {"color": "#3B5BDB", "ratio": 0.423, "ring_r": 13.0, "arm": 8.0, "thick": 5.5, "label": "Loading",
       "fit": False}
EASE = "ease-in-out"
ROW = {"A": (-38, 0), "B": (0, 0), "C": (38, 0)}
DURATIONS = {"orbit": 6, "swap": 6.5, "satellites": 6.5, "breathe": 6.5, "bloom": 6.5, "hop": 1.1}


# ----------------------------------------------------------------- shapes
def ring(cls, r_out):
    thick = r_out * (1 - CFG["ratio"])
    return (f'<circle class="{cls}" r="{r_out - thick / 2:.2f}" fill="none" '
            f'stroke="{CFG["color"]}" stroke-width="{thick:.2f}"/>')


def cross(cls, arm, th):
    h = th / 2
    d = (f"M{-arm:g} {-h:g}H{-h:g}V{-arm:g}H{h:g}V{-h:g}H{arm:g}V{h:g}H{h:g}V{arm:g}"
         f"H{-h:g}V{h:g}H{-arm:g}Z")
    return f'<path class="{cls}" d="{d}" fill="{CFG["color"]}"/>'


# ----------------------------------------------------------------- helpers
def tf(x, y, r, s):
    return f"translate({x:.2f}px, {y:.2f}px) rotate({r:g}deg) scale({s:.3f})"


def smooth(s):
    """Smoothstep: eases the start and end of the orbit samples."""
    return s * s * (3 - 2 * s)


def polar(radius, angle):
    t = math.radians(angle)
    return radius * math.cos(t), radius * math.sin(t), math.sin(t)


def header(view="0 0 120 100"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}" role="img" '
            f'aria-label="{CFG["label"]}"><title>{CFG["label"]}</title>\n')


def half_size(elem):
    """Half of the largest extent of a ring or cross element (cross: arm length times the diagonal)."""
    m = re.search(r'r="([\d.]+)".*stroke-width="([\d.]+)"', elem)
    if m:
        return float(m.group(1)) + float(m.group(2)) / 2
    m = re.search(r'd="M-([\d.]+)', elem)
    return float(m.group(1)) * 1.42 if m else 0


def fitted_view(marks, margin=2.0):
    """viewBox (centered on the origin) that contains every piece in every keyframe."""
    xs, ys = [], []
    for _, elem, frames in marks:
        h = half_size(elem)
        for _, x, y, _, s, _ in frames:
            xs += [x - h * s, x + h * s]
            ys += [y - h * s, y + h * s]
    x0, y0, x1, y1 = min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin
    return f"{x0:.1f} {y0:.1f} {x1 - x0:.1f} {y1 - y0:.1f}"


def assemble(marks, dur):
    """marks: list of (class, svg_element, frames); frame = (pct, x, y, rot, scale, timing)."""
    fit = CFG["fit"]
    view = fitted_view(marks) if fit else "0 0 120 100"
    css = ["  .m { transform-box: fill-box; transform-origin: 50% 50%; }"]
    els = []
    for name, elem, frames in marks:
        frames = sorted(frames, key=lambda f: f[0])
        lines = [f"    {p:g}% {{ transform: {tf(x, y, r, s)}; animation-timing-function: {tm}; }}"
                 for p, x, y, r, s, tm in frames]
        css.append(f"  @keyframes k-{name} {{\n" + "\n".join(lines) + "\n  }")
        _, x, y, r, s, _ = frames[0]
        css.append(f"  .{name} {{ transform: {tf(x, y, r, s)}; animation: k-{name} {dur}s infinite; }}")
        els.append("  " + elem)
    css.append("  @media (prefers-reduced-motion: reduce) { .m { animation: none !important; } }")
    group = "<g>" if fit else '<g transform="translate(60 50)">'
    return (header(view) + "<style>\n" + "\n".join(css) + "\n</style>\n"
            + group + "\n" + "\n".join(els) + "\n</g>\n</svg>\n")


def trio():
    ro, arm, th = CFG["ring_r"], CFG["arm"], CFG["thick"]
    return {"A": ("ma", ring("m ma", ro)), "B": ("mb", cross("m mb", arm, th)), "C": ("mc", ring("m mc", ro))}


# ----------------------------------------------------------------- recipes
def orbit():
    ANG = {"A": 200, "B": 320, "C": 80}
    R, N = 24, 24
    marks = []
    for d, (name, elem) in trio().items():
        rx, ry = ROW[d]
        is_cross = d == "B"
        x, y, sn = polar(R, ANG[d])
        k = [(0, rx, ry, 0, 1, EASE), (6, rx, ry, 0, 1, EASE),
             (14, x, y, 90 if is_cross else 0, 1 + .25 * sn, "linear")]
        for i in range(1, N + 1):
            s = smooth(i / N)
            x, y, sn = polar(R, ANG[d] + 360 * s)
            k.append((14 + 56 * i / N, x, y, (90 + 360 * s) if is_cross else 0, 1 + .25 * sn,
                      "linear" if i < N else EASE))
        k += [(82, rx, ry, 540 if is_cross else 0, 1, EASE), (100, rx, ry, 540 if is_cross else 0, 1, EASE)]
        marks.append((name, elem, k))
    return assemble(marks, DURATIONS["orbit"])


def swap():
    L, M, Rr = -38, 0, 38
    steps = [(5, 30), (32, 57), (59, 84)]
    plan = {  # (x_start, x_end, kind) per step
        "A": [(L, M, "straight"), (M, Rr, "straight"), (Rr, L, "over")],
        "B": [(M, Rr, "straight"), (Rr, L, "under"), (L, M, "straight")],
        "C": [(Rr, L, "over"), (L, M, "straight"), (M, Rr, "straight")],
    }
    marks = []
    for d, (name, elem) in trio().items():
        is_cross = d == "B"
        k = [(0, plan[d][0][0], 0, 0, 1, EASE)]
        rot = 0
        for (p0, p1), (x0, x1, kind) in zip(steps, plan[d]):
            delta = (90 if kind == "straight" else 180) if is_cross else 0
            rot += delta
            if kind == "straight":
                k += [(p0, x0, 0, rot - delta, 1, EASE), (p1, x1, 0, rot, 1, EASE)]
            else:
                sign = -1 if kind == "over" else 1
                n = 10
                k.append((p0, x0, 0, rot - delta, 1, "linear"))
                for i in range(1, n + 1):
                    u = smooth(i / n)
                    y = sign * (38 if sign < 0 else 34) * math.sin(math.pi * u)
                    sc = 1 + (.12 if sign > 0 else -.3) * math.sin(math.pi * u)
                    k.append((p0 + (p1 - p0) * i / n, x0 + (x1 - x0) * u, y, rot - delta + delta * u, sc,
                              "linear" if i < n else EASE))
        k.append((100, plan[d][-1][1], 0, rot, 1, EASE))
        marks.append((name, elem, k))
    return assemble(marks, DURATIONS["swap"])


def satellites():
    N = 48
    marks = []
    for d, (name, elem) in trio().items():
        rx, ry = ROW[d]
        if d == "B":
            k = [(0, 0, 0, 0, 1, EASE), (6, 0, 0, 0, 1, EASE)]
            for i in range(1, N + 1):
                s = smooth(i / N)
                k.append((6 + 78 * i / N, 0, 0, 720 * s, 1 + .1 * math.sin(math.pi * s),
                          "linear" if i < N else EASE))
            k.append((100, 0, 0, 720, 1, EASE))
        else:
            th0 = 180 if d == "A" else 0
            k = [(0, rx, ry, 0, 1, EASE), (6, rx, ry, 0, 1, "linear")]
            for i in range(1, N + 1):
                t = math.radians(th0 + 720 * smooth(i / N))
                k.append((6 + 78 * i / N, 38 * math.cos(t), 28 * math.sin(t), 0, 1 + .22 * math.sin(t),
                          "linear" if i < N else EASE))
            k.append((100, rx, ry, 0, 1, EASE))
        marks.append((name, elem, k))
    return assemble(marks, DURATIONS["satellites"])


def breathe():
    ANG = {"A": 200, "B": 320, "C": 80}
    N = 32
    marks = []
    for d, (name, elem) in trio().items():
        rx, ry = ROW[d]
        is_cross = d == "B"
        x, y, sn = polar(22, ANG[d])
        k = [(0, rx, ry, 0, 1, EASE), (6, rx, ry, 0, 1, EASE),
             (14, x, y, 90 if is_cross else 0, 1 + .25 * sn, "linear")]
        for i in range(1, N + 1):
            u = i / N
            s = smooth(u)
            x, y, sn = polar(22 + 10 * math.sin(math.pi * u), ANG[d] + 360 * s)
            k.append((14 + 58 * u, x, y, (90 + 360 * s) if is_cross else 0, 1 + .25 * sn,
                      "linear" if i < N else EASE))
        k += [(84, rx, ry, 540 if is_cross else 0, 1, EASE), (100, rx, ry, 540 if is_cross else 0, 1, EASE)]
        marks.append((name, elem, k))
    return assemble(marks, DURATIONS["breathe"])


def bloom():
    ease_out = "cubic-bezier(.2,.7,.3,1)"
    RADIUS = 34
    sat_ring = CFG["ring_r"] * 7 / 13      # satellite ring
    sat_arm = CFG["arm"] * 6 / 8           # satellite cross
    sat_th = CFG["thick"] * 4 / 5.5
    css, els = [], []
    for k in range(6):
        base = -90 + 60 * k
        is_ring = k % 2 == 0
        x0, y0, _ = polar(RADIUS, base)
        fr = [(0, 0, 0, 0, 0, EASE), (6, 0, 0, 0, 0, ease_out), (22, x0, y0, 0, 1, "linear")]
        n = 8
        for i in range(1, n + 1):
            x, y, _ = polar(RADIUS, base + 90 * i / n)
            fr.append((22 + 40 * i / n, x, y, 0 if is_ring else 90 * i / n, 1, "linear" if i < n else EASE))
        fr += [(78, 0, 0, 0 if is_ring else 90, 0, EASE), (100, 0, 0, 0 if is_ring else 90, 0, EASE)]
        lines = [f"    {p:g}% {{ transform: {tf(x, y, r, s)}; animation-timing-function: {tm}; }}"
                 for p, x, y, r, s, tm in fr]
        css.append(f"  @keyframes s{k} {{\n" + "\n".join(lines) + "\n  }")
        css.append(f"  .s{k} {{ transform: scale(0); animation: s{k} 6.5s infinite; animation-delay: {k * 0.07:.2f}s; }}")
        els.append("  " + (ring(f"m s{k}", sat_ring) if is_ring else cross(f"m s{k}", sat_arm, sat_th)))
    css.append("  @keyframes center {\n    0%, 6% { transform: scale(1); } 14% { transform: scale(1.15); }"
               " 22%, 70% { transform: scale(1); }\n    78% { transform: scale(1.12); } 90%, 100% { transform: scale(1); }\n  }")
    css.append("  .center { animation: center 6.5s ease-in-out infinite; }")
    css.append("  @media (prefers-reduced-motion: reduce) { .m { animation: none !important; } }")
    reach = 34 + sat_ring + 3          # orbit radius + satellite ring + margin
    view = f"{-reach:.1f} {-reach:.1f} {2 * reach:.1f} {2 * reach:.1f}" if CFG["fit"] else "0 0 120 100"
    group = "<g>" if CFG["fit"] else '<g transform="translate(60 50)">'
    return (header(view) + "<style>\n  .m { transform-box: fill-box; transform-origin: 50% 50%; }\n"
            + "\n".join(css) + "\n</style>\n" + group + "\n" + "\n".join(els)
            + "\n  " + ring("m center", CFG["ring_r"]) + "\n</g>\n</svg>\n")


def hop():
    ro, arm, th = CFG["ring_r"], CFG["arm"], CFG["thick"]
    fit = CFG["fit"]
    reach_x = 38 + ro * 1.05 + 2
    view = f"{-reach_x:.1f} {-(24 + ro * 1.05 + 4):.1f} {2 * reach_x:.1f} {ro * 1.05 + 24 + ro * 1.05 + 8:.1f}" if fit else "0 0 120 100"
    group = "<g>" if fit else '<g transform="translate(60 62)">'
    return (header(view) + "<style>\n"
            "  .m { transform-box: fill-box; transform-origin: 50% 100%; }\n"
            "  .ma { animation: hop-ring 1.1s ease-in-out infinite; }\n"
            "  .mb { animation: hop-cross 1.1s ease-in-out infinite; animation-delay: -.12s; }\n"
            "  .mc { animation: hop-ring 1.1s ease-in-out infinite; animation-delay: -.24s; }\n"
            "  @keyframes hop-ring {\n    0%, 100% { transform: translateY(0px) scale(1.05, .95); }\n"
            "    50% { transform: translateY(-24px) scale(.97, 1.04); }\n  }\n"
            "  @keyframes hop-cross {\n    0%, 100% { transform: translateY(0px) rotate(0deg) scale(1.05, .95); }\n"
            "    50% { transform: translateY(-24px) rotate(90deg) scale(.97, 1.04); }\n  }\n"
            "  @media (prefers-reduced-motion: reduce) { .m { animation: none; } }\n</style>\n"
            + group + "\n"
            f'  <g transform="translate(-38 0)">{ring("m ma", ro)}</g>\n'
            f'  <g>{cross("m mb", arm, th)}</g>\n'
            f'  <g transform="translate(38 0)">{ring("m mc", ro)}</g>\n</g>\n</svg>\n')


RECIPES = {"orbit": orbit, "swap": swap, "satellites": satellites, "breathe": breathe,
           "bloom": bloom, "hop": hop}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recipe", choices=sorted(RECIPES))
    ap.add_argument("--out", help="output .svg path")
    ap.add_argument("--list", action="store_true", help="list recipes and cycle durations")
    ap.add_argument("--color", default=CFG["color"], help="fill color, e.g. '#3B5BDB' or 'currentColor' (inline use only)")
    ap.add_argument("--label", default=CFG["label"], help="accessible name (aria-label and <title>)")
    ap.add_argument("--fit", action="store_true",
                    help="tight viewBox around the moving pieces: bigger pieces at 16-32 px (the default 120x100 box leaves margin)")
    ap.add_argument("--hole-ratio", type=float, default=CFG["ratio"], help="hole radius / outer radius of the ring")
    ap.add_argument("--ring-radius", type=float, default=CFG["ring_r"], help="outer radius of the large ring")
    ap.add_argument("--arm", type=float, default=CFG["arm"], help="half length of a cross arm")
    ap.add_argument("--thickness", type=float, default=CFG["thick"], help="thickness of a cross arm")
    a = ap.parse_args()
    if a.list or not a.recipe:
        for name in RECIPES:
            print(f"{name:10s} {DURATIONS[name]}s")
        if not a.recipe:
            return
    if not a.out:
        sys.exit("pass --out")
    CFG.update(color=a.color, ratio=a.hole_ratio, ring_r=a.ring_radius, arm=a.arm, thick=a.thickness,
               label=a.label, fit=a.fit)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(RECIPES[a.recipe]())
    print("ok", a.out, f"(cycle of {DURATIONS[a.recipe]}s)")


if __name__ == "__main__":
    main()
