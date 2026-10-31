---
name: logo-to-ai-loading-icon
description: Create an animated SVG loading icon (pure CSS, no JavaScript) for AI chat and agent responses from a brand logo, in the style of the "thinking" indicators of AI assistants, with symbols derived from the logo (ring, cross) that move and return to rest. Use whenever the user asks for a loading, spinner, "thinking" or "typing" indicator for an AI chat, assistant or agent, wants to turn a logo into a loader, wants brand shapes moving while a response is generated, or needs a WebP or GIF fallback for such an icon, even if they do not say "SVG".
license: MIT
compatibility: Needs Python 3 with Playwright (Chromium) and Pillow for the measure, render and export scripts (pip install -r requirements.txt, then playwright install chromium). Writing the SVG itself needs nothing else.
metadata:
  updated: "2026-10-31"
---

# Logo to AI loading icon

Produces one `.svg` file, animated only with CSS, that works in `<img>`, as a CSS `background` and inline. It is the "AI is working" indicator of a chat or agent UI, built from the user's own logo.

## Principles (they came from real review rounds)

- **Return to rest, then repeat.** Frame 0% and frame 100% are identical, with a short pause at rest. AI assistant indicators animate, settle, and animate again.
- **Continuity beats spectacle.** Prefer movements where pieces change without cuts and the loop closes smoothly.
- **No tile, no text.** Brand color directly on the shapes. When the user wants a symbol, derive shapes from the logo (the ring of an "o", the cross of a "t") and do not show the letters.
- **Pieces never merge.** Pieces cross each other through depth (scale and paint order), never by overlapping at the same position. A cross entering a ring was rejected in review.
- **Show options.** For open requests, generate 3 to 6 variants and render a contact sheet so the user can choose.

## Workflow

1. **Understand the input.** Read `references/logo-input.md`. Measure the logo with `python scripts/measure_logo.py logo.svg --split`. Note the shapes, the color and the suggested viewBox. Ask where the icon will live (size, light or dark background) only if you cannot tell.
2. **Choose a recipe.** Read `references/recipes.md`. Six recipes exist: `hop`, `breathe`, `orbit`, `swap`, `satellites`, `bloom`. The "States" and "Legibility at small sizes" sections map them to waiting states and sizes.
3. **Generate.** `python scripts/generate_symbols.py --recipe bloom --out loader.svg --color "#RRGGBB"`. Match the brand with `--hole-ratio`, `--ring-radius`, `--arm`, `--thickness`. Add `--fit` when the icon is sized by height (inline next to text), `--label` for the accessible name, and generate a second file with a light `--color` for dark backgrounds. `--list` shows the recipes and their cycle durations.
4. **Validate.** `python scripts/validate_svg.py loader.svg` (an ERROR blocks; fix WARN; read INFO).
5. **Look at the frames.** `python scripts/render_frames.py loader.svg --duration <cycle seconds> --sheet sheet.png`, then actually open the sheet and follow `references/verification.md`. For small icons add `--sizes 16,24,32,48`.
6. **Deliver.** Send the `.svg` (and the dark variant). State the cycle length and how to use it (`<img src>`). If the destination cannot show animated SVG (email, some apps), export with `python scripts/export_fallback.py loader.svg --duration <s> --format webp --out loader.webp`.

`assets/examples/` has one generated example per recipe, fit and dark variants, a sample logo to practice measuring, and `chat-bubble.html`, which shows the loader inside light and dark chat bubbles.

## SVG versus animated WebP

SVG with CSS is the default for the web: a few KB, sharp at any size, honors `prefers-reduced-motion`. Use animated WebP only when the destination cannot render animated SVG. GIF is the last resort because its transparency is 1-bit.

## Rules for writing the SVG

- `viewBox` is required; add a `<title>` with a readable name and `role="img"`.
- Animations live in `@keyframes` inside a `<style>` in the SVG itself, with `animation-iteration-count: infinite`.
- Every shape that rotates or scales needs `transform-box: fill-box` together with `transform-origin`.
- Include an `@media (prefers-reduced-motion: reduce)` block that stops the animation at the resting frame.
- Use `animation-timing-function` per interval (ease-in-out for movements, linear only for continuous rotation).
- Brand color as hex; offer a light variant for dark backgrounds. `currentColor` only works for inline SVG, not for `<img>`.

## References

- `references/logo-input.md`: measure and decompose the logo, and map it to generator options.
- `references/recipes.md`: recipe catalog, durations, legibility at small sizes, states, design preferences.
- `references/pitfalls.md`: defects that already happened and how to fix them.
- `references/verification.md`: how to check the animation without watching it in real time.
