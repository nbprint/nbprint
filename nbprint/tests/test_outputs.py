from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from nbprint.cli import run
from nbprint.config.outputs.nbconvert import NBConvertOutputs


def test_outputs():
    config = run(str(Path(__file__).parent / "files" / "basic.yaml"), dry_run=True)
    assert config.outputs.naming == "{{name}}-{{date}}-{{datetime}}-{{uuid}}-{{sha}}"
    path = config.outputs.run(config=config, gen=config.generate())
    assert len(path.name) == 150
    today = datetime.now()
    assert path.stem.startswith(
        f"basic-{today.year}-{'0' + str(today.month) if today.month < 10 else today.month}-{'0' + str(today.day) if today.day < 10 else today.day}"
    )


class TestNbconvertConfigPassthrough:
    """Generic nbconvert/traitlets configuration passthrough."""

    def test_default_is_empty(self):
        out = NBConvertOutputs(naming="{{name}}", root=".pytest_cache/cfg")
        assert out.nbconvert_config == {}

    def test_format_scalar_args(self):
        args = NBConvertOutputs._format_nbconvert_config_args(
            {
                "WebPDFExporter.page_render_timeout": 5000,
                "TemplateExporter.exclude_input": True,
                "HTMLExporter.embed_images": False,
                "Exporter.some_name": "hello",
                "Exporter.some_float": 1.5,
            }
        )
        assert "--WebPDFExporter.page_render_timeout=5000" in args
        assert "--TemplateExporter.exclude_input=True" in args
        assert "--HTMLExporter.embed_images=False" in args
        assert "--Exporter.some_name=hello" in args
        assert "--Exporter.some_float=1.5" in args

    def test_format_container_args_json_encoded(self):
        args = NBConvertOutputs._format_nbconvert_config_args(
            {
                "TemplateExporter.extra_template_basedirs": ["a", "b"],
            }
        )
        assert args == ['--TemplateExporter.extra_template_basedirs=["a", "b"]']

    def test_format_nested_namespaces_flatten(self):
        """Nested dicts flatten into dotted traitlet paths (matches hydra overrides)."""
        args = NBConvertOutputs._format_nbconvert_config_args(
            {
                "WebPDFExporter": {"page_render_timeout": 5000, "allow_chromium_download": True},
                "TemplateExporter": {"exclude_input": True},
            }
        )
        assert "--WebPDFExporter.page_render_timeout=5000" in args
        assert "--WebPDFExporter.allow_chromium_download=True" in args
        assert "--TemplateExporter.exclude_input=True" in args

    def test_flat_and_nested_are_equivalent(self):
        flat = NBConvertOutputs._format_nbconvert_config_args({"WebPDFExporter.page_render_timeout": 5000})
        nested = NBConvertOutputs._format_nbconvert_config_args({"WebPDFExporter": {"page_render_timeout": 5000}})
        assert flat == nested == ["--WebPDFExporter.page_render_timeout=5000"]

    def test_format_empty(self):
        assert NBConvertOutputs._format_nbconvert_config_args({}) == []

    def test_config_reaches_convert_command(self):
        """nbconvert_config entries are appended to the conversion argv."""
        config = run(str(Path(__file__).parent / "files" / "basic.yaml"), dry_run=True)
        config.outputs.execute = False
        config.outputs.nbconvert_config = {"WebPDFExporter.page_render_timeout": 4200}

        with patch("nbprint.config.outputs.nbconvert._run_nbconvert") as mock_run:
            config.outputs.run(config=config, gen=config.generate())

        # The (only) nbconvert invocation is the conversion pass.
        assert mock_run.call_count == 1
        argv = mock_run.call_args[0][0]
        assert "--WebPDFExporter.page_render_timeout=4200" in argv

    def test_config_from_cli_override(self):
        """Nested nbconvert_config is settable via a hydra/lerna CLI override."""
        config = run(
            "examples/basic.yaml",
            ["++outputs.nbconvert_config.WebPDFExporter.page_render_timeout=8000"],
            dry_run=True,
        )
        assert config.outputs.nbconvert_config == {"WebPDFExporter": {"page_render_timeout": 8000}}
        argv = NBConvertOutputs._format_nbconvert_config_args(config.outputs.nbconvert_config)
        assert argv == ["--WebPDFExporter.page_render_timeout=8000"]


class TestNbconvertConfigManagedTraitGuard:
    """nbconvert_config rejects traits that nbprint already manages."""

    @pytest.mark.parametrize(
        ("config", "field_hint"),
        [
            ({"ExecutePreprocessor.enabled": True}, "execute"),
            ({"ExecutePreprocessor.timeout": 60}, "timeout"),
            ({"NbConvertApp.export_format": "pdf"}, "target"),
            ({"TemplateExporter.template_name": "custom"}, "template"),
            ({"NbConvertApp.output_base": "foo"}, "naming"),
        ],
    )
    def test_managed_trait_flat_rejected(self, config, field_hint):
        with pytest.raises(ValidationError) as exc:
            NBConvertOutputs(naming="{{name}}", root=".pytest_cache/guard", nbconvert_config=config)
        assert field_hint in str(exc.value)

    def test_managed_trait_nested_rejected(self):
        with pytest.raises(ValidationError) as exc:
            NBConvertOutputs(
                naming="{{name}}",
                root=".pytest_cache/guard",
                nbconvert_config={"ExecutePreprocessor": {"enabled": True}},
            )
        assert "execute" in str(exc.value)

    def test_managed_alias_form_rejected(self):
        with pytest.raises(ValidationError) as exc:
            NBConvertOutputs(naming="{{name}}", root=".pytest_cache/guard", nbconvert_config={"to": "html"})
        assert "target" in str(exc.value)

    def test_assignment_is_guarded(self):
        """validate_assignment means the guard also fires on direct attribute sets."""
        out = NBConvertOutputs(naming="{{name}}", root=".pytest_cache/guard")
        with pytest.raises(ValidationError):
            out.nbconvert_config = {"ExecutePreprocessor.enabled": True}

    def test_safe_trait_alongside_is_fine(self):
        out = NBConvertOutputs(
            naming="{{name}}",
            root=".pytest_cache/guard",
            nbconvert_config={"WebPDFExporter.page_render_timeout": 5000},
        )
        assert out.nbconvert_config == {"WebPDFExporter.page_render_timeout": 5000}
