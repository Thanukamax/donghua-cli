"""Single source of truth for color + glyph + spacing tokens.

Both Rich-based output (theme.py / app.py / ui.py) and Textual CSS (tui.py)
read from here. No raw hex literals belong anywhere else in the codebase.
"""

from __future__ import annotations

# ── Color tokens (8 semantic roles) ──────────────────────────────────────
# Tokens, not colors. Use the role, not the hex.

# Jade + gold + ink, matching the landing page and the seal motif rather than
# the generic slate/amber this used to be. Contrast is measured against
# `surface`, not eyeballed; the ratios below are WCAG against #0a0f0d.
PALETTE: dict[str, str] = {
    # Text hierarchy — warm parchment on ink, not blue-grey on navy.
    "text":         "#f5efe2",   # parchment · 16.9:1 AAA
    "text_muted":   "#a8b5ab",   # secondary / labels · 9.1:1 AAA
    "text_faint":   "#7d8a80",   # captions / meta · 5.4:1 AA
    "text_ghost":   "#4a5750",   # rules + disabled — decoration, not copy
    # Surfaces
    "surface":      "#0a0f0d",   # app background (site bg exactly)
    "surface_alt":  "#111a16",   # status bar, headers, raised
    "border":       "#22302a",   # default border / hairline
    # Accents — used sparingly. One accent per screen, ideally.
    "accent":       "#d4af37",   # brand gold · 9.2:1 AAA
    "accent_alt":   "#6f9183",   # brand jade · 5.6:1 AA — focus ring, alive
    # The brand seal-red (#c3272b) is only 3.4:1 on this background, which is
    # too low for error copy, so `danger` is that hue lifted to stay readable.
    "danger":       "#e05561",   # errors only — never decorative · 5.2:1 AA
}

# Aliases for legacy theme tokens (kept so external callers don't break)
ALIASES: dict[str, str] = {
    "jade":         PALETTE["accent_alt"],
    "gold":         PALETTE["accent"],
    "silver":       PALETTE["text"],
    "steel":        PALETTE["text_muted"],
    "dim":          PALETTE["text_faint"],
    "ghost":        PALETTE["text_ghost"],
    "void":         PALETTE["border"],
    "border":       PALETTE["accent_alt"],
    "title":        f"bold {PALETTE['accent']}",
    "subtitle":     PALETTE["text"],
    "accent":       PALETTE["accent"],
    "success":      PALETTE["accent_alt"],
    "error":        PALETTE["danger"],
    "warning":      PALETTE["accent"],
    "info":         PALETTE["text"],
}


def hex_for(token: str) -> str:
    """Return the hex code for a semantic token. KeyError on unknown."""
    return PALETTE[token]


# ── Glyph budget (5 max, fixed meanings) ─────────────────────────────────

GLYPH = {
    "ok":      "✓",   # ✓ success
    "fail":    "✗",   # ✗ error
    "pending": "⟳",   # ⟳ in-flight
    "play":    "▶",   # ▶ playing
    "star":    "★",   # ★ bookmark / pinned
}

# Separators — single style each, used consistently
SEP_THIN = "│"        # │ vertical
SEP_DOT  = "·"        # · soft inline
RULE     = "─"        # ─ horizontal rule


# ── Spacing scale (3 steps) ──────────────────────────────────────────────
# For Textual CSS: padding/margin should pick from this set, not invent values.

PAD_TIGHT   = "0 1"
PAD_DEFAULT = "0 2"
PAD_LOOSE   = "1 3"


# ── Textual theme ────────────────────────────────────────────────────────
# Derived from the tokens above so Textual CSS and Rich markup cannot drift.
# Textual generates the shade ramps ($primary-lighten-2, $secondary-muted, …)
# and the contrast-safe text tokens ($text, $text-muted, $text-disabled) from
# these, which is the tedious half of a palette we no longer hand-maintain.


def build_theme():
    """The app's Textual ``Theme``. Imported lazily so palette.py stays
    dependency-free for the Rich-only code paths (app.py, ui.py, doctor.py)."""
    from textual.theme import Theme

    return Theme(
        name="wuxia-night",
        primary=PALETTE["accent"],        # gold — selection, keys, primary CTA
        secondary=PALETTE["accent_alt"],  # jade — focus, "alive"
        accent=PALETTE["accent"],
        foreground=PALETTE["text"],
        background=PALETTE["surface"],
        surface=PALETTE["surface_alt"],
        panel=PALETTE["border"],
        success=PALETTE["accent_alt"],
        warning=PALETTE["accent"],
        error=PALETTE["danger"],
        dark=True,
        variables={
            # Wuxia-specific tokens, namespaced so they read as ours.
            "text-faint": PALETTE["text_faint"],
            "text-ghost": PALETTE["text_ghost"],
            # Focus treatment: unfocused borders recede, focused ones take jade.
            "border": PALETTE["accent_alt"],
            "border-blurred": PALETTE["border"],
            # Footer / scrollbars, themed rather than restated per-widget.
            "footer-key-foreground": PALETTE["accent"],
            "footer-description-foreground": PALETTE["text_faint"],
            "scrollbar": PALETTE["border"],
            "scrollbar-hover": PALETTE["accent_alt"],
            "scrollbar-active": PALETTE["accent"],
            "scrollbar-background": PALETTE["surface"],
            "block-cursor-background": PALETTE["accent_alt"],
            "block-cursor-foreground": PALETTE["surface"],
            "block-cursor-text-style": "bold",
            "input-selection-background": f"{PALETTE['accent_alt']} 35%",
        },
    )
