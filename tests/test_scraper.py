"""Tests for scraper logic -- title normalization, matching, episode merging."""


from donghua_cli.scraper import _normalize_title, _titles_match, _merge_episodes, _merge_results


class TestNormalizeTitle:
    def test_strips_english_subbed(self):
        assert _normalize_title("Soul Land English Subbed") == "soul land"
        assert _normalize_title("Soul Land English Sub") == "soul land"

    def test_strips_year_brackets(self):
        assert _normalize_title("Martial Peak [2024]") == "martial peak"
        assert _normalize_title("Martial Peak (2024)") == "martial peak"

    def test_normalizes_season_notation(self):
        # Season info must be preserved (so S1 and S5 stay distinct) but
        # variants — "Season 2", "S2", "Season 04" — all canonicalise to
        # the same "season N" form so cross-source merging still works.
        assert _normalize_title("Soul Land Season 2") == "soul land season 2"
        assert _normalize_title("Soul Land S2") == "soul land season 2"
        assert _normalize_title("Soul Land Season 04") == "soul land season 4"

    def test_lowercases(self):
        assert _normalize_title("BATTLE Through The HEAVENS") == "battle through the heavens"

    def test_collapses_whitespace(self):
        assert _normalize_title("  Soul   Land  ") == "soul land"


class TestTitlesMatch:
    def test_exact_match(self):
        assert _titles_match("Soul Land", "Soul Land")

    def test_subbed_suffix(self):
        assert _titles_match("Soul Land", "Soul Land English Subbed")

    def test_year_difference(self):
        assert _titles_match("Martial Peak (2024)", "Martial Peak [2024]")

    def test_clearly_different(self):
        assert not _titles_match("Soul Land", "Martial Peak")

    def test_same_season_match(self):
        assert _titles_match("Soul Land Season 1", "Soul Land S1 Subbed")
        assert _titles_match("Soul Land Season 04", "Soul Land Season 4")

    def test_different_seasons_do_not_match(self):
        # Regression: "season 4" and "season 5" otherwise hit a 0.97 ratio
        # and silently merge — that was the BTTH "no S1-S4 results" bug.
        assert not _titles_match(
            "Battle Through The Heavens Season 4",
            "Battle Through The Heavens Season 5",
        )
        assert not _titles_match("Soul Land Season 1", "Soul Land Season 2")

    def test_bare_title_does_not_merge_into_numbered_season(self):
        # A landing page without a season marker is a distinct entry from a
        # numbered season page on the same series.
        assert not _titles_match(
            "Battle Through the Heavens",
            "Battle Through the Heavens Season 5",
        )


class TestMergeEpisodes:
    def test_merges_same_episode_number(self):
        raw = [
            ("ld", "Episode 1", "http://ld/ep1"),
            ("ax", "Episode 1 Sub", "http://ax/ep1"),
            ("ld", "Episode 2", "http://ld/ep2"),
        ]
        episodes = _merge_episodes(raw)
        assert len(episodes) == 2
        assert len(episodes[0].urls) == 2  # ep 1 on both sources
        assert len(episodes[1].urls) == 1  # ep 2 only on ld

    def test_sorted_by_number(self):
        raw = [
            ("ld", "Episode 5", "http://ld/ep5"),
            ("ld", "Episode 1", "http://ld/ep1"),
            ("ld", "Episode 3", "http://ld/ep3"),
        ]
        episodes = _merge_episodes(raw)
        assert [e.number for e in episodes] == [1, 3, 5]

    def test_unknown_numbers_kept_separate(self):
        # Pages whose episode number can't be parsed return the 999999
        # sentinel. They MUST NOT all collapse into one phantom row.
        raw = [
            ("ld", "Trailer", "http://ld/trailer"),
            ("ld", "Behind the Scenes", "http://ld/bts"),
            ("ld", "Episode 1", "http://ld/ep1"),
        ]
        episodes = _merge_episodes(raw)
        # 1 known + 2 unknowns, all distinct
        assert len(episodes) == 3
        assert episodes[0].number == 1
        # Unknowns sort to the end and each keeps a single URL.
        assert all(len(e.urls) == 1 for e in episodes[1:])


class TestMergeResults:
    def test_deduplicates_across_sources(self):
        raw = [
            ("ld", "Soul Land (2024)", "http://ld/soul-land", None),
            ("ax", "Soul Land (2024) Subbed", "http://ax/soul-land", None),
        ]
        merged = _merge_results(raw)
        assert len(merged) == 1
        assert len(merged[0].urls) == 2

    def test_keeps_different_series(self):
        raw = [
            ("ld", "Soul Land", "http://ld/soul-land", None),
            ("ld", "Martial Peak", "http://ld/martial-peak", None),
        ]
        merged = _merge_results(raw)
        assert len(merged) == 2

    def test_cover_url_propagates(self):
        raw = [
            ("ld", "Soul Land", "http://ld/soul-land", "http://ld/cover.jpg"),
            ("ax", "Soul Land", "http://ax/soul-land", None),
        ]
        merged = _merge_results(raw)
        assert len(merged) == 1
        assert merged[0].cover_url == "http://ld/cover.jpg"

    def test_keeps_seasons_distinct(self):
        # The full BTTH-style case: every season has an entry on each
        # source. Seasons must remain distinct in the merged output, with
        # same-season URLs from different sources aggregated together.
        raw = [
            ("ld", "Battle Through The Heavens Season 5", "http://ld/btth-s5", None),
            ("ax", "Battle Through The Heavens Season 5", "http://ax/btth-s5", None),
            ("ld", "Battle Through The Heavens Season 4", "http://ld/btth-s4", None),
            ("ax", "Battle Through the Heavens Season 4", "http://ax/btth-s4", None),
            ("ld", "Battle Through The Heavens Season 1", "http://ld/btth-s1", None),
        ]
        merged = _merge_results(raw)
        titles = sorted(s.title for s in merged)
        assert len(merged) == 3, f"expected S1, S4, S5 distinct; got {titles}"
        by_season = {s.title: s for s in merged}
        s5_key = next(t for t in by_season if "Season 5" in t)
        s4_key = next(t for t in by_season if "Season 4" in t)
        # Same-season URLs from different sources DO aggregate.
        assert set(by_season[s5_key].urls.keys()) == {"ld", "ax"}
        assert set(by_season[s4_key].urls.keys()) == {"ld", "ax"}
