

class TestClip:
    """Titles must show a cut, not look like corrupt data."""

    def test_short_text_is_untouched(self):
        from donghua_cli.tui import _clip
        assert _clip("Perfect World", 32) == "Perfect World"

    def test_long_text_gets_an_ellipsis(self):
        from donghua_cli.tui import _clip
        got = _clip("Battle Through The Heavens Season 5 Special", 32)
        assert got.endswith("…")

    def test_result_never_exceeds_the_budget(self):
        # The ellipsis lives inside `width`, so a fixed-width column cannot be
        # blown out by one cell.
        from donghua_cli.tui import _clip
        for w in (1, 5, 12, 32, 60):
            assert len(_clip("x" * 200, w)) <= w


class TestTheme:
    """The Textual theme and the Rich palette must not drift apart."""

    def test_theme_is_built_from_the_palette(self):
        from donghua_cli.palette import PALETTE, build_theme
        t = build_theme()
        assert t.primary == PALETTE["accent"]
        assert t.secondary == PALETTE["accent_alt"]
        assert t.background == PALETTE["surface"]
        assert t.error == PALETTE["danger"]

    def test_css_carries_no_format_placeholders(self):
        # The CSS used to be a .format() template, which meant every literal
        # brace had to be doubled. Guard against that pattern coming back.
        import re
        from donghua_cli.tui import WUXIA_CSS
        assert "{{" not in WUXIA_CSS
        assert not re.search(r"\{[a-z_]+\}", WUXIA_CSS)
