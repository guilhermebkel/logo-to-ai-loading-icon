# Known pitfalls

Each of these happened during development and was fixed. `scripts/validate_svg.py` catches several.

| Symptom | Cause | Fix |
|---|---|---|
| An arc or dot shows up at the start of the cycle | `stroke-dasharray: 100` with `pathLength="100"` repeats every 200; an offset of 102 exposes the last 2% | Use `stroke-dasharray: 100 200` |
| A dot on a hidden stroke | `stroke-linecap: round` with `stroke-dashoffset` | Offset ≥ 102, or `butt` caps on thin lines |
| A trail extends ahead of the head | Trail arcs with the wrong offset | Use a fixed offset on the trail and remove positive delays |
| The fill runs ahead of the pen | Fill and stroke use different timings | Same timing for both; delay the fill wipe |
| A hairline seam at the top of a closed circle used as a mask | The closed circle ends exactly on the seam | Extend the mask path with an extra arc past the seam |
| Rings look too flat when hopping | Too much squash | Keep `scale(1.05, .95)` and `scale(.97, 1.04)` |
| Pieces overlap when crossing on arcs | Same arc height for every piece | Different heights (38 and 34) and scales (−0.3 / +0.12) |
| A ring and a cross overlap on an ellipse | Not enough depth | Ellipse `ry` 28 and scale 0.22 |
| A shape rotates around the viewBox corner | `transform-origin` without `transform-box` | Always add `transform-box: fill-box` |
| A jump when the loop restarts | The 0% state differs from the 100% state | A cross is symmetric every 90°: rotate only by multiples of 90°, and compare the first and last frames |
| A cross fused with a ring | The cross passes through the center of the ring | Separate trajectories, or make the cross pass in front with a larger scale. Fusing was rejected in review |
| No movement when used in `<img>` | The animation depends on JavaScript or complex `var()` | Pure CSS, with generated numbers in the keyframes |
| Different result in Safari | Animated `clipPath` renders differently | Test in Safari, or prefer `mask` / `transform` |
| The icon is invisible on dark backgrounds | A dark brand color on a dark chat | Generate a second file with a light `--color` |
| The icon is too small inline | The default viewBox leaves margin | Size by height and generate with `--fit` |

## Rules of thumb

- Generate keyframes with a script when there is an orbit (many points). Do not write them by hand.
- Keep each file under about 20 KB (reduce samples and decimals).
- Never copy an animated asset from a third party. Use it only as a motion reference.
