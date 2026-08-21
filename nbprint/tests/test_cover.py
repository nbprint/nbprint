"""Tests for the default cover layout.

``ContentCover`` used to be a tag-only stub, so every consumer wrote the same
centred-column block itself. These cover the default being present, being
overridable, and not disturbing the tag contract.
"""

from nbprint.config.content.cover import DEFAULT_COVER_CSS, ContentCover


class TestDefaultCss:
    def test_cover_ships_a_default_layout(self):
        assert ContentCover().css == DEFAULT_COVER_CSS

    def test_default_centres_a_constrained_column(self):
        css = ContentCover().css
        assert "margin: auto;" in css
        assert "text-align: center;" in css
        assert "flex-direction: column;" in css

    def test_tunables_are_custom_properties_with_fallbacks(self):
        css = ContentCover().css
        for prop, fallback in (
            ("--nbprint-cover-width", "75%"),
            ("--nbprint-cover-logo-width", "200px"),
            ("--nbprint-cover-title-gap", "10px"),
            ("--nbprint-cover-subtitle-gap", "5px"),
        ):
            assert f"var({prop}, {fallback})" in css

    def test_default_does_not_use_important(self):
        # The default is the base layer, so it should lose to anything a
        # consumer sets rather than having to be fought with !important.
        assert "!important" not in ContentCover().css


class TestOverride:
    def test_explicit_css_replaces_the_default_outright(self):
        cover = ContentCover(css=":scope { color: red; }")
        assert cover.css == ":scope { color: red; }"
        assert "margin: auto;" not in cover.css

    def test_empty_css_is_respected(self):
        assert ContentCover(css="").css == ""


class TestTagContract:
    def test_cover_tag_is_added_when_tags_are_supplied(self):
        assert "nbprint:content:cover" in ContentCover(tags=["custom"]).tags

    def test_existing_tags_are_preserved(self):
        assert "custom" in ContentCover(tags=["custom"]).tags

    def test_cover_tag_is_not_duplicated(self):
        tags = ContentCover(tags=["nbprint:content:cover"]).tags
        assert tags.count("nbprint:content:cover") == 1

    def test_default_css_does_not_depend_on_the_tag_validator(self):
        # The tag validator does not run for a default-constructed instance
        # (pydantic does not validate defaults), so the styling must not be
        # routed through it.
        assert ContentCover().css == DEFAULT_COVER_CSS
