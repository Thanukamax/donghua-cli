"""Single source of truth for color + glyph + spacing tokens.

Both Rich-based output (theme.py / app.py / ui.py) and Textual CSS (tui.py)
read from here. No raw hex literals belong anywhere else in the codebase.
"""

from __future__ import annotations

# ── Color tokens (8 semantic roles) ──────────────────────────────────────
# Tokens, not colors. Use the role, not the hex.

PALETTE: dict[str, str] = {
    # Text hierarchy
    "text":         "#e2e8f0",   # primary readable text
    "text_muted":   "#94a3b8",   # secondary / labels
    "text_faint":   "#64748b",   # captions / meta
    "text_ghost":   "#475569",   # separators, rules, disabled
    # Surfaces
    "surface":      "#0c0e1a",   # app background
    "surface_alt":  "#111827",   # status bar, headers, raised
    "border":       "#1e293b",   # default border / hairline
    # Accents — used sparingly. One accent per screen, ideally.
    "accent":       "#fbbf24",   # selected, important keys, primary CTA
    "accent_alt":   "#5eead4",   # focus ring, success, "alive" pulse
    "danger":       "#f43f5e",   # errors only — never decorative
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
