# Recipe catalog

Contents: [Design preferences](#design-preferences) · [Recipes](#recipes) · [Legibility at small sizes](#legibility-at-small-sizes) · [Rhythm](#rhythm) · [States](#states)

## Design preferences

These came from real review rounds. Treat them as defaults until the user says otherwise.

- **Continuity.** The loop ends exactly where it started. Frame 0% and frame 100% are identical, with a short pause at rest so the restart reads clearly.
- **Return to rest, then repeat.** Pieces move away from the resting row, do something, and come back, like the indicators of AI chat products.
- **No tile, no text.** Use the brand color directly on the shapes, with no background tile and no letters, so the icon works on any chat background.
- **Pieces never merge.** A cross entering a ring was rejected. Pieces cross each other through depth (scale and paint order), never by overlapping at the same position.
- **Show options.** For open requests, generate 3 to 6 variants and render a contact sheet so the user can pick.

## Recipes

All recipes come from `scripts/generate_symbols.py`. Resting layout: ring at (-38, 0), cross at (0, 0), ring at (38, 0). Default viewBox `0 0 120 100`, content centered at `translate(60 50)`.

| Recipe | Cycle | Motion | Best use |
|---|---|---|---|
| `hop` | 1.1 s | Ring, cross and ring hop in a wave; the cross turns 90° per hop; small squash on landing | Short "thinking" indicator, inline next to text |
| `breathe` | 6.5 s | The three pieces orbit while the orbit radius grows from 22 to 32 and back | Calm waiting state |
| `orbit` | 6 s | Row → triangle → one full turn (cross spinning) → row | General-purpose loader |
| `swap` | 6.5 s | The pieces trade places along arcs (38 up, 34 down, scale −0.3 / +0.12) | Medium sizes, 24 px and up |
| `satellites` | 6.5 s | Two rings circle the cross on a 38×28 ellipse | Medium sizes |
| `bloom` | 6.5 s | One ring sends out six smaller pieces (radius 34) that spread and return | "Generating", large sizes |

Options that matter: `--color` (use a light color for dark backgrounds), `--fit` (tight viewBox, better when you size the icon by height), `--label` (accessible name), and the proportion options in `references/logo-input.md`.

## Legibility at small sizes

Measured by rendering each recipe at 16, 24, 32 and 48 px wide (`render_frames.py --sizes 16,24,32,48`), mid-motion:

| Recipe | 16 px | 24 px | 32 px | 48 px |
|---|---|---|---|---|
| `hop` | dots only | rings readable | clear | clear |
| `swap` | dots only | rings readable | clear | clear |
| `satellites` | dots only | readable | clear | clear |
| `orbit` | dots only | readable, cross small | clear | clear |
| `breathe` | dots only | readable, cross small | clear | clear |
| `bloom` | cluster of dots | reads as a busy cluster | clear, cross vs ring distinct | clear |

Rules of thumb:

- Below 24 px the ring hole and the cross arms disappear; the icon reads as moving dots. That is acceptable for a pure activity indicator, but not as a recognizable brand mark.
- Row recipes are 3 pieces wide, so their pieces are small when the icon is sized by width. Size by height and use `--fit` to gain 10 to 25%.
- For 16 px icons prefer `hop`, which has the fewest moving parts.
- `bloom` needs 32 px or more to tell crosses from rings.

## Rhythm

- Short cycles (about 1 s) for "thinking"; long cycles (6 to 6.5 s) for slow, ambient states.
- A pause of 5% to 15% of the cycle at rest.
- Continuous rotation may be `linear`; everything else uses ease-in-out per interval.
- Orbits use sampled keyframes (12 to 48 points with smoothstep), not a single `rotate`, so speed varies naturally.
- Depth: scale by sin(θ) (bigger in front, smaller behind) so pieces pass each other without touching.

## States

A chat product often has more than one waiting state. A reasonable mapping:

| State | Suggested recipe |
|---|---|
| Sent, waiting for the first token | `hop` |
| Thinking / reasoning | `breathe` or `orbit` |
| Generating a long answer | `bloom` |

This is a suggestion, not a rule. The same brand shapes across states keep the identity consistent.
