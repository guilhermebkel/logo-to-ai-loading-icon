# Input: measure and decompose the logo

Before animating, find out what the logo is made of.

## Steps

1. Open the SVG. Look for `<g transform>`, a background (a rect or circle that fills everything) and how many `<path>` elements there are.
2. Run `python scripts/measure_logo.py logo.svg --split`.
   - `local` is the box in the element's own coordinate system: use it when writing CSS inside the same `<g transform>`.
   - `in_viewBox` is the box in the file's viewBox space: use it to place things outside the group.
   - `--split` separates the `M…Z` subpaths. Two letters in one `<path>`, or a ring (outer contour + hole), show up separately.
3. Use the suggested viewBox (and `--margin`) when you animate only the shapes without the background tile.
4. Note the fill color and whether a version for dark backgrounds exists.

## From logo to symbols

The generator draws a **ring** and a **cross** because those two shapes recur in many logos (an "o", a dot with a hole, a "t", a plus sign). To match your brand:

| Logo feature | Measure | Generator option |
|---|---|---|
| Ring or round letter with a hole | hole width / outer width | `--hole-ratio` (default 0.423) |
| Ring size relative to the cross | outer radius, in the same units | `--ring-radius` (default 13) |
| Cross (letter with a crossbar, plus sign) | half length of an arm, arm thickness | `--arm` (default 8), `--thickness` (default 5.5) |
| Brand color | fill of the shapes | `--color` |

Example: a logo whose "o" measures 53.8 wide with a 22.7 wide hole has a hole ratio of 22.7 / 53.8 = 0.42.

If the logo has no ring or cross, keep the proportions but pick the closest primitive shapes (a dot, a bar). The choreography does not depend on the exact shape, only on the pieces staying clear of each other.

## Other logos

- Single-shape logo: animate that shape (pulse, breathe) instead of splitting it into pieces.
- Text-only logo: ask the user for a symbol or a key letter; with no recognizable shape, a plain brand-colored dot sequence still works as an AI loading icon.
- Keep the original brand rules: never distort the final static mark, and ship a static end frame for reduced motion.
