"""Tests for page-region running elements and first-page region suppression."""

from pydantic import Field

from nbprint import PageGlobal, PageRegion, RunningElement
from nbprint.config.core.page import PageNumber, PageRegionContent


def make_page(**kwargs) -> PageGlobal:
    page = PageGlobal(**kwargs)
    page.render()
    return page


class TestRunningElement:
    def test_content_defaults_to_the_named_element(self):
        el = RunningElement(name="footerLogo", selector=".footer-logo")
        assert el.content == "element(footerLogo)"

    def test_explicit_content_is_left_alone(self):
        el = RunningElement(name="footerLogo", selector=".footer-logo", content="element(other)")
        assert el.content == "element(other)"

    def test_margin_box_pulls_in_the_element(self):
        page = make_page(bottom_left=PageRegion(content=RunningElement(name="footerLogo", selector=".footer-logo")))
        assert "@bottom-left { content: element(footerLogo); }" in page.bottom_left.css

    def test_source_element_is_made_running(self):
        page = make_page(bottom_left=PageRegion(content=RunningElement(name="footerLogo", selector=".footer-logo")))
        assert ".footer-logo { position: running(footerLogo); }" in page.css

    def test_running_rule_is_not_rooted_at_body(self):
        # Paged.js hides the source element by matching this rule against the
        # parsed content fragment, which holds the body's children rather than
        # the body itself. A body-rooted selector matches nothing there, so the
        # element is never hidden and leaks into the flow.
        page = make_page(bottom_left=PageRegion(content=RunningElement(name="footerLogo", selector=".footer-logo")))
        assert "body.pagedjs .footer-logo { position: running" not in page.css

    def test_running_rule_does_not_force_the_element_visible(self):
        # Paged.js hides the source element with an inline `display: none`, which
        # an !important declaration here would outrank.
        page = make_page(bottom_left=PageRegion(content=RunningElement(name="footerLogo", selector=".footer-logo")))
        assert "position: running(footerLogo); display: block !important;" not in page.css

    def test_source_element_is_hidden_outside_pagedjs(self):
        page = make_page(bottom_left=PageRegion(content=RunningElement(name="footerLogo", selector=".footer-logo")))
        assert "body:not(.pagedjs) .footer-logo { display: none !important; }" in page.css

    def test_source_css_is_page_level_not_region_level(self):
        # A region's own CSS is emitted as cell CSS, which the template wraps in
        # @scope; a rule addressing body from there can never match.
        page = make_page(bottom_left=PageRegion(content=RunningElement(name="footerLogo", selector=".footer-logo")))
        assert "position: running" not in page.bottom_left.css
        assert "position: running" in page.css

    def test_selector_is_used_verbatim(self):
        page = make_page(top_right=PageRegion(content=RunningElement(name="mark", selector="#brand .mark")))
        assert "#brand .mark { position: running(mark); }" in page.css
        assert "body:not(.pagedjs) #brand .mark { display: none !important; }" in page.css

    def test_source_css_is_not_duplicated(self):
        page = make_page(bottom_left=PageRegion(content=RunningElement(name="footerLogo", selector=".footer-logo")))
        assert page.css.count("position: running(footerLogo)") == 1


class PageWithDefaultRegions(PageGlobal):
    """A Page subclass supplying its regions the way a consumer does."""

    bottom_left: PageRegion = Field(default_factory=lambda: PageRegion(content=RunningElement(name="footerLogo", selector=".footer-logo")))
    bottom: PageRegion = Field(default_factory=PageRegion)
    top_right_corner: PageRegion = Field(default_factory=PageRegion)


class TestRegionsSuppliedAsDefaults:
    """Regions set as Pydantic field defaults skip the `mode="before"` validators."""

    def test_margin_box_rule_is_still_emitted(self):
        page = PageWithDefaultRegions()
        page.render()
        assert "@bottom-left { content: element(footerLogo); }" in page.bottom_left.css

    def test_region_is_named(self):
        assert PageWithDefaultRegions().top_right_corner._region == "top-right-corner"

    def test_edge_regions_keep_their_centre_names(self):
        assert "@bottom-center { content: counter(page); }" in PageWithDefaultRegions().bottom.css

    def test_corner_region_is_not_confused_with_its_edge(self):
        assert "@top-right-corner { content: counter(page); }" in PageWithDefaultRegions().top_right_corner.css

    def test_rule_is_not_duplicated_across_instances(self):
        PageWithDefaultRegions()
        assert PageWithDefaultRegions().bottom.css.count("@bottom-center") == 1


class TestPlainRegionsUnaffected:
    def test_page_number_region_emits_no_extra_css(self):
        page = make_page(bottom=PageRegion())
        assert page.bottom.css == "@page { @bottom-center { content: counter(page); } }"

    def test_region_css_hook_defaults_to_empty(self):
        assert PageRegionContent(content="x").region_css() == ""
        assert PageNumber().region_css() == ""


class TestFirstPageSuppression:
    def test_off_by_default(self):
        assert "pagedjs_first_page" not in make_page().css

    def test_hides_every_margin_edge_on_the_first_page(self):
        css = make_page(suppress_first_page_regions=True).css
        for edge in ("top", "bottom", "left", "right"):
            assert f".pagedjs_first_page .pagedjs_margin-{edge}" in css
        assert "display: none !important;" in css

    def test_render_is_idempotent(self):
        page = make_page(suppress_first_page_regions=True)
        page.render()
        assert page.css.count(".pagedjs_first_page .pagedjs_margin-top") == 1
