# API Reference

## Configuration

```{eval-rst}
.. currentmodule:: nbprint.config.core

.. autosummary::
   :toctree: _build

    Configuration

    Parameters
    Context
    Content
    Page
    Outputs
```

## CLI

```{eval-rst}
.. currentmodule:: nbprint.cli

.. autosummary::
   :toctree: _build

    run
    hydra
    hydra_explain
```

## Hydra

```{eval-rst}
.. currentmodule:: nbprint.config.hydra

.. autosummary::
   :toctree: _build

    load_config
```

## Implementations

```{eval-rst}
.. currentmodule:: nbprint.config.core

.. autosummary::
   :toctree: _build

    PapermillParameters

.. currentmodule:: nbprint.config.content

.. autosummary::
   :toctree: _build

    ContentCode
    ContentMarkdown
    ContentImage
    ContentTableOfContents
    ContentLayout
    ContentInlineLayout
    ContentFlexColumnLayout
    ContentFlexRowLayout
    ContentPageBreak

.. currentmodule:: nbprint.config.outputs

.. autosummary::
   :toctree: _build

    NBConvertOutputs
    PDFOutputs
    NotebookOutputs
    HTMLOutputs
    WebHTMLOutputs
    NBConvertShortCircuitOutputs

    EmailOutputs
    SMTP

.. currentmodule:: nbprint.models

.. autosummary::
   :toctree: _build

    LoggingConfig
    PandasDisplayConfiguration
    PlotlyRendererConfiguration
    SeabornDisplayConfiguration
```
