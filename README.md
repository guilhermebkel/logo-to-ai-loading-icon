# logo-to-ai-loading-icon

An agent skill that turns your brand logo into an **animated SVG loading icon for AI chat and agent UIs**, in the style of the "thinking" indicators of AI assistants: shapes derived from your logo (a ring, a cross) that move, return to rest and repeat. Pure CSS, no JavaScript, works in `<img>`.

<table>
  <tr>
    <td align="center"><img src="skills/logo-to-ai-loading-icon/assets/examples/symbols-hop.svg" width="150" alt="hop"><br><code>hop</code> · 1.1 s</td>
    <td align="center"><img src="skills/logo-to-ai-loading-icon/assets/examples/symbols-breathe.svg" width="150" alt="breathe"><br><code>breathe</code> · 6.5 s</td>
    <td align="center"><img src="skills/logo-to-ai-loading-icon/assets/examples/symbols-bloom.svg" width="150" alt="bloom"><br><code>bloom</code> · 6.5 s</td>
  </tr>
  <tr>
    <td align="center"><img src="skills/logo-to-ai-loading-icon/assets/examples/symbols-orbit.svg" width="150" alt="orbit"><br><code>orbit</code> · 6 s</td>
    <td align="center"><img src="skills/logo-to-ai-loading-icon/assets/examples/symbols-swap.svg" width="150" alt="swap"><br><code>swap</code> · 6.5 s</td>
    <td align="center"><img src="skills/logo-to-ai-loading-icon/assets/examples/symbols-satellites.svg" width="150" alt="satellites"><br><code>satellites</code> · 6.5 s</td>
  </tr>
</table>

The colors above are a fictional brand. You pass your own (`--color`) and the proportions of your logo.

## Install

```bash
npx skills add guilhermebkel/logo-to-ai-loading-icon -g
```

Without `-g` it installs only in the current project. The CLI asks which agents should get the skill.

The scripts need Python 3 with Playwright and Pillow (the installer does not set up Python dependencies):

```bash
pip install -r requirements.txt   # in the installed skill folder
playwright install chromium
```

## Use

Ask your agent in plain words, with your logo attached:

> Make a loading icon for my AI chat's "thinking" state from this logo. Brand color is #3B5BDB. I also need a version for dark mode.

The skill measures the logo, picks a recipe (or shows you a few), generates the SVG, validates it, renders frames to check the choreography and the legibility at small sizes, and delivers the files. For destinations that cannot show animated SVG it can export an animated WebP or GIF.

You can also run the scripts directly (from `skills/logo-to-ai-loading-icon/`):

```bash
python scripts/measure_logo.py logo.svg --split               # shapes, boxes, suggested viewBox
python scripts/generate_symbols.py --recipe bloom --out loader.svg --color "#3B5BDB"
python scripts/generate_symbols.py --recipe hop --fit --color "#E8EAF6" --out loader-dark.svg
python scripts/validate_svg.py loader.svg                     # known pitfalls
python scripts/render_frames.py loader.svg --duration 6.5 --sheet sheet.png
python scripts/render_frames.py loader.svg --duration 6.5 --fractions 0.3 --sizes 16,24,32,48 --sheet small.png
python scripts/export_fallback.py loader.svg --duration 6.5 --format webp --out loader.webp
```

`skills/logo-to-ai-loading-icon/assets/examples/chat-bubble.html` shows the loader inside light and dark chat bubbles.

## What makes it different

- **Made for AI loading states.** Recipes map to waiting states (sent, thinking, generating) and are checked at 16 to 48 px, in light and dark.
- **Return to rest.** Every loop starts and ends in the same pose, with a pause, like the indicators of AI assistants.
- **Symbols derived from your logo** (ring, cross) instead of a generic spin or pulse, with no tile and no text.
- **Verified by frames.** A validator for known pitfalls and a frame renderer that sets the animation clock directly, so what you check is what the browser plays.

For general logo reveals, intros and splash animations (stroke draw-on, mask wipes, morphs, Lottie), a general-purpose skill such as [logo-animation](https://github.com/iart-ai/motion-design-skills) is a better fit.

## Repository layout

```
skills/logo-to-ai-loading-icon/   # the skill installed by `npx skills add`
  SKILL.md  scripts/  references/  assets/examples/  evals/
```

## License

MIT. See [LICENSE](LICENSE).
