#!/usr/bin/env python3
"""Check an animated SVG against the known pitfalls (see references/pitfalls.md).

Usage: python validate_svg.py file.svg [other.svg ...]
Output: a list of ERROR / WARN / INFO lines. Exit code 1 if there is any ERROR.
"""
import re
import sys
import xml.dom.minidom
from pathlib import Path


def check(path):
    findings = []
    text = Path(path).read_text(encoding="utf-8")
    try:
        xml.dom.minidom.parseString(text)
    except Exception as e:  # malformed XML
        return [("ERROR", f"invalid XML: {e}")]

    if "viewBox" not in text:
        findings.append(("ERROR", "the <svg> has no viewBox"))
    if "<title" not in text:
        findings.append(("WARN", "no <title>; screen readers get no name"))
    if "aria-label" not in text and "<title" not in text:
        findings.append(("WARN", "no aria-label and no title"))

    animated = bool(re.search(r"animation\s*:|animation-name|<animate", text))
    if animated and "prefers-reduced-motion" not in text:
        findings.append(("WARN", "animated but does not handle prefers-reduced-motion"))

    # pathLength=100 with a single dasharray value: the pattern repeats every 200 and the end of the stroke leaks at the start
    if re.search(r"stroke-dasharray\s*[:=]\s*[\"']?\s*100\s*[;\"'}]", text):
        findings.append(("WARN", "single-value stroke-dasharray (100): use '100 200' so the end of the stroke does not leak into the start of the cycle"))

    if re.search(r"stroke-linecap\s*:\s*round", text) and "stroke-dashoffset" in text:
        findings.append(("INFO", "round linecap with dashoffset: the hidden stroke may leave a dot at the start; use offset >= 102 or butt caps on thin lines"))

    if "transform-origin" in text and "transform-box" not in text:
        findings.append(("WARN", "transform-origin without transform-box: fill-box; the origin will be the viewBox origin, not the shape"))

    if re.search(r"@keyframes[^{]*\{[^@]*var\(--", text):
        findings.append(("INFO", "var(--x) inside keyframes works in current browsers, but generated numeric values are more robust"))

    if re.search(r"<clipPath[^>]*>.*?class=", text, flags=re.S) and animated:
        findings.append(("INFO", "animated element inside a clipPath: rendering differs between browsers, test in Safari"))

    if "currentColor" not in text and re.search(r"(fill|stroke)\s*[:=]\s*[\"']?#[0-9a-fA-F]{3,6}", text):
        findings.append(("INFO", "hard-coded hex color: it only suits one kind of background; consider a dark variant or currentColor"))

    size = len(text.encode("utf-8"))
    if size > 20000:
        findings.append(("WARN", f"large file ({size} bytes); reduce keyframe samples or decimal places"))
    else:
        findings.append(("INFO", f"{size} bytes"))
    return findings


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    failed = False
    for p in sys.argv[1:]:
        print(f"== {p}")
        for level, msg in check(p):
            print(f"  [{level}] {msg}")
            failed = failed or level == "ERROR"
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
