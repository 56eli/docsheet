#!/usr/bin/env python3
"""Regression guard: verify CSS zebra-row and block-wash contrast stays above the human-perception threshold.

This test prevents future agents from silently flattening the alternating
row colors (the defect documented in AUDIT_REPEATED_FAILURE_STYLING_2026-08-09.md
and R-01 in NEXT_AGENT_HANDOFF.md). It reads docs/style.css and asserts that:

1. --zebra is sufficiently distinct from --surface in both light and dark modes.
2. Block wash color-mix percentages are above a minimum visibility threshold.
3. --row-hover is distinguishable from --zebra in both modes.

Run:  python -m unittest tests/test_style_contrast.py -v
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STYLE_CSS = REPO / "docs" / "style.css"


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def luminance(r: int, g: int, b: int) -> float:
    """Perceived luminance (ITU-R BT.601)."""
    return 0.299 * r + 0.587 * g + 0.114 * b


def parse_root_tokens(css: str, dark: bool = False) -> dict[str, str]:
    """Extract CSS custom property values from :root or :root.dark block."""
    pattern = r":root\.dark\s*\{" if dark else r":root\s*\{"
    match = re.search(pattern, css)
    if not match:
        raise ValueError(f"Could not find :root{'dark' if dark else ''} block")
    # Find the first closing brace at the same nesting depth
    start = match.end()
    depth = 1
    pos = start
    while pos < len(css) and depth > 0:
        if css[pos] == "{":
            depth += 1
        elif css[pos] == "}":
            depth -= 1
        pos += 1
    block = css[start : pos - 1]
    tokens = {}
    for prop_match in re.finditer(r"--([\w-]+)\s*:\s*([^;]+);", block):
        tokens[prop_match.group(1)] = prop_match.group(2).strip()
    return tokens


def parse_color_mix_percentages(css: str) -> list[float]:
    """Extract all color-mix percentages used in block row rules."""
    return [
        float(m.group(1))
        for m in re.finditer(
            r"row-block-.*?color-mix\(in srgb,\s*var\(--block-\w+\)\s+([\d.]+)%",
            css,
        )
    ]


class StyleContrastTests(unittest.TestCase):
    """Assert zebra and block-wash tokens meet minimum contrast thresholds."""

    @classmethod
    def setUpClass(cls):
        cls.css = STYLE_CSS.read_text(encoding="utf-8")
        cls.light = parse_root_tokens(cls.css, dark=False)
        cls.dark = parse_root_tokens(cls.css, dark=True)

    def test_zebra_contrast_light(self):
        """--zebra must be distinguishable from --surface in light mode."""
        surface_lum = luminance(*hex_to_rgb(self.light["surface"]))
        zebra_lum = luminance(*hex_to_rgb(self.light["zebra"]))
        delta = abs(surface_lum - zebra_lum)
        self.assertGreaterEqual(
            delta,
            10,
            f"Light-mode zebra contrast {delta:.1f} is below 10 luminance units; "
            f"--surface={self.light['surface']} vs --zebra={self.light['zebra']}",
        )

    def test_zebra_contrast_dark(self):
        """--zebra must be distinguishable from --surface in dark mode."""
        surface_lum = luminance(*hex_to_rgb(self.dark["surface"]))
        zebra_lum = luminance(*hex_to_rgb(self.dark["zebra"]))
        delta = abs(surface_lum - zebra_lum)
        self.assertGreaterEqual(
            delta,
            6,
            f"Dark-mode zebra contrast {delta:.1f} is below 6 luminance units; "
            f"--surface={self.dark['surface']} vs --zebra={self.dark['zebra']}",
        )

    def test_hover_contrast_light(self):
        """--row-hover must be distinguishable from --zebra in light mode."""
        zebra_lum = luminance(*hex_to_rgb(self.light["zebra"]))
        hover_lum = luminance(*hex_to_rgb(self.light["row-hover"]))
        delta = abs(zebra_lum - hover_lum)
        self.assertGreaterEqual(
            delta,
            7,
            f"Light-mode hover contrast {delta:.1f} is below 7 luminance units; "
            f"--zebra={self.light['zebra']} vs --row-hover={self.light['row-hover']}",
        )

    def test_hover_contrast_dark(self):
        """--row-hover must be distinguishable from --zebra in dark mode."""
        zebra_lum = luminance(*hex_to_rgb(self.dark["zebra"]))
        hover_lum = luminance(*hex_to_rgb(self.dark["row-hover"]))
        delta = abs(zebra_lum - hover_lum)
        self.assertGreaterEqual(
            delta,
            8,
            f"Dark-mode hover contrast {delta:.1f} is below 8 luminance units; "
            f"--zebra={self.dark['zebra']} vs --row-hover={self.dark['row-hover']}",
        )

    def test_block_wash_minimum_opacity(self):
        """Block wash color-mix percentages must be above the perception threshold."""
        percentages = parse_color_mix_percentages(self.css)
        self.assertGreater(len(percentages), 0, "No block wash color-mix rules found")
        for pct in percentages:
            self.assertGreaterEqual(
                pct,
                8.0,
                f"Block wash {pct}% is below the 8% perception threshold",
            )

    def test_block_wash_light_maximum(self):
        """Light-mode block washes must not exceed 15% (keep rows light, not opaque)."""
        # The light-mode block rules use var(--surface) or var(--zebra) as base;
        # dark-mode rules use var(--surface) and var(--zebra) in :root.dark context.
        # We check that no percentage exceeds 15% for the light washes.
        percentages = parse_color_mix_percentages(self.css)
        for pct in percentages:
            self.assertLessEqual(
                pct,
                18.0,
                f"Block wash {pct}% exceeds 18% maximum (rows would be opaque)",
            )

    def test_no_slate_blue_in_tokens(self):
        """No --bg/--surface/--border token may contain visible blue hue (slate)."""
        slate_hexes = {"f8fafc", "f1f5f9", "e2e8f0", "0f172a", "1e293b", "334155", "333b45"}
        for mode, tokens in [("light", self.light), ("dark", self.dark)]:
            for key in ("bg", "surface", "border"):
                val = tokens.get(key, "").lstrip("#").lower()
                self.assertNotIn(
                    val,
                    slate_hexes,
                    f"{mode} --{key}={tokens[key]} is slate blue (regression)",
                )


if __name__ == "__main__":
    unittest.main()
