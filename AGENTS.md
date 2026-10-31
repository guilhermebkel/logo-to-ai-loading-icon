# AGENTS.md

This repository is an agent skill, `logo-to-ai-loading-icon`: it turns a brand logo into an animated SVG loading icon (pure CSS) for AI chat and agent UIs. There is no app, build step or database.

## Layout

- `skills/logo-to-ai-loading-icon/`: the skill. This folder is what `npx skills add` installs.
  - `SKILL.md`: instructions and frontmatter (`name`, `description`, `license`, `compatibility`, `metadata`).
  - `scripts/`: `generate_symbols.py`, `validate_svg.py`, `render_frames.py`, `export_fallback.py`, `measure_logo.py`.
  - `references/`: detailed docs loaded on demand.
  - `assets/examples/`: generated example SVGs, a sample logo and `chat-bubble.html`.
  - `evals/`: test cases (`prompt.md`, `case.yaml`, `graders/`, `files/`).
- `README.md`, `LICENSE`, `.github/workflows/ci.yml`: repository-level files.

## Releases

Releases are manual: Actions → Release → Run workflow on `main`, choosing `patch`, `minor`, `major` or `none` (release the current version as is). The workflow runs the CI checks, bumps `metadata.version` and `metadata.updated` in `SKILL.md`, commits `release: vX.Y.Z [skip ci]`, tags `vX.Y.Z`, attaches the packaged `.skill` and creates the GitHub Release with generated notes. Do not edit `metadata.version` by hand.

## Commands

```bash
pip install -r skills/logo-to-ai-loading-icon/requirements.txt
playwright install chromium

cd skills/logo-to-ai-loading-icon
python scripts/generate_symbols.py --list
python scripts/generate_symbols.py --recipe bloom --out /tmp/bloom.svg
python scripts/validate_svg.py assets/examples/*.svg
python scripts/render_frames.py assets/examples/symbols-hop.svg --duration 1.1 --sheet /tmp/sheet.png
```

## Rules

- Everything in the repository is in English.
- Never add a real brand's logo, name or color to examples or docs. Examples use a fictional brand (`#3B5BDB`).
- Do not copy assets or code from third parties. Other work is a motion reference only.
- Examples in `assets/examples/` are generated. After changing `generate_symbols.py`, regenerate them (CI fails if they drift) and run `validate_svg.py`.
- Changing an animation means looking at rendered frames (`render_frames.py --sheet`), not only reading the CSS. The first and last frames of a loop must be identical.
- Keep `SKILL.md` under 500 lines and put detail in `references/`. Frontmatter keys are limited to `name`, `description`, `license`, `compatibility`, `allowed-tools` and `metadata`; metadata values are strings. Update `metadata.updated` when the skill changes.
