"""Tests for scraper logic -- title normalization, matching, episode merging."""


from donghua_cli.scraper import _normalize_title, _titles_match, _merge_episodes, _merge_results


class TestNormalizeTitle:
    def test_strips_english_subbed(self):
        assert _normalize_title("Soul Land English Subbed") == "soul land"
        assert _normalize_title("Soul Land English Sub") == "soul land"

    def test_strips_year_brackets(self):
        assert _normalize_title("Martial Peak [2024]") == "martial peak"
        assert _normalize_title("Martial Peak (2024)") == "martial peak"

    def test_strips_season(self):
        assert _normalize_title("Soul Land Season 2") == "soul land"
        assert _normalize_title("Soul Land S2") == "soul land"

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

    def test_season_match(self):
        assert _titles_match("Soul Land Season 1", "Soul Land S1 Subbed")


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


class TestMergeResults:
    def test_deduplicates_across_sources(self):
        raw = [
            ("ld", "Soul Land (2024)", "http://ld/soul-land"),
            ("ax", "Soul Land (2024) Subbed", "http://ax/soul-land"),
        ]
        merged = _merge_results(raw)
        assert len(merged) == 1
        assert len(merged[0].urls) == 2

    def test_keeps_different_series(self):
        raw = [
            ("ld", "Soul Land", "http://ld/soul-land"),
            ("ld", "Martial Peak", "http://ld/martial-peak"),
        ]
        merged = _merge_results(raw)
        assert len(merged) == 2
