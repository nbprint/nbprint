<a href="https://github.com/nbprint/nbprint#gh-light-mode-only">
  <img src="https://github.com/nbprint/nbprint/raw/main/docs/img/logo-light.png?raw=true#gh-light-mode-only" alt="nbprint" width="400"></a>
</a>
<a href="https://github.com/nbprint/nbprint#gh-dark-mode-only">
  <img src="https://github.com/nbprint/nbprint/raw/main/docs/img/logo-dark.png?raw=true#gh-dark-mode-only" alt="nbprint" width="400"></a>
</a>
<br/>

A framework for building print media with [`nbconvert`](https://nbconvert.readthedocs.io).

[![Build Status](https://github.com/nbprint/nbprint/actions/workflows/build.yaml/badge.svg?branch=main&event=push)](https://github.com/nbprint/nbprint/actions/workflows/build.yaml)
[![Coverage](https://codecov.io/gh/nbprint/nbprint/branch/main/graph/badge.svg?token=ag2j2TV2wE)](https://app.codecov.io/gh/nbprint/nbprint/tree/main)
[![GitHub issues](https://img.shields.io/github/issues/nbprint/nbprint.svg)](https://github.com/nbprint/nbprint/issues)
[![License](https://img.shields.io/github/license/nbprint/nbprint)](https://github.com/nbprint/nbprint)

## Installation

Install with `pip`:

```bash
pip install nbprint
```

Install with `conda`

```bash
conda install nbprint -c conda-forge
```

## Background

Jupyter Notebooks are widely used for reports via [`nbconvert`](https://nbconvert.readthedocs.io/en/latest/), but most development work has been on enabling building interactive websites. The goal of `nbprint` is to focus on print-oriented workflows, e.g. PDF, by leveraging new developments in `nbconvert` and the [`pagedjs`](https://pagedjs.org) print-oriented layout library.

For a deeper dive, see [the documentation](<>).

## Quickstart

`nbprint` provides an `nbconvert` template and a [configuration framework](<>).
The simplest example can be run with defaults by calling the `nbprint` executable on an existing notebook:

```bash
nbprint examples/basic.ipynb
```

This CLI supports configuration-driven customization with [hydra](https://hydra.cc) syntax:

```bash
nbprint examples/basic.ipynb +nbprint.name=test ++nbprint.outputs.target=pdf

# First cell is papermill-style parameters
nbprint examples/parameters.ipynb +nbprint.parameters.a=test

# Overlay a config group, e.g. title and table of contents
nbprint examples/basic.ipynb nbprint/content/frontmatter=nbprint/title_toc
```

```mermaid
graph TB
    nb("notebook<br>(.ipynb)")
    nbc{nbconvert}
    nbct[/nbprint <br> template/]
    pjs[/paged.js <br> layout engine/]
    o@{ shape: doc, label: "output (html,pdf,etc)" }

    nb e2@--->nbc
    e2@{animate: true}

    nbct --> nbc
    pjs --- nbct

    nbc e3@-->o
    e3@{animate: true}
```

### Outputs

`nbprint` can produce a variety of outputs based on [`nbconvert`](https://nbconvert.readthedocs.io/en/latest/).
It can also postprocess these outputs based on content, to e.g. email a report if a certain cell returns `True`, as a simple example.

With [`hydra`](https://hydra.cc), its easy for us to mix-and-match configuration for content, outputs, layout, and more.

```bash
# Create HTML from notebook as-is
nbprint examples/basic.ipynb

# Create HTML using hydra to overlay title page and table-of-contents
nbprint examples/basic.ipynb nbprint/content/frontmatter=nbprint/title_toc

# Create PDF via WebPDF by using hydra to swap out outputs type
nbprint examples/basic.ipynb nbprint/outputs=nbprint/pdf

# Create PDF via WebPDF same as above by using hydra to tweak the default output target
nbprint examples/basic.ipynb ++nbprint.outputs.target=webpdf
```

For more information, see [the architecture documentation](<>).

### Multiruns

See [#ccflow-integration](#ccflow-integration) below.

### Configuration

See the [configuration framework documentation](<>) for more information on building YAML-based report workflows with `hydra`.

## ccflow integration

`nbprint` is compatible with [ccflow](https://github.com/point72/ccflow) callable models.
`nbprint` outputs like `NBConvertOutputs` inherit from [`ccflow.ResultsBase`](https://github.com/Point72/ccflow/wiki/Workflows#result-type), and `nbprint` parameters like `Parameters` inherit from [`ccflow.ContextBase`](https://github.com/Point72/ccflow/wiki/Workflows#context).

```bash
nbprint-cc +nbprint.name=test +context=[]
```

## Development

**Warning**: This project is under active development, so all APIs are subject to change!

## License

This software is licensed under the Apache 2.0 license. See the [LICENSE](LICENSE) file for details.

> [!NOTE]
> This library was generated using [copier](https://copier.readthedocs.io/en/stable/) from the [Base Python Project Template repository](https://github.com/python-project-templates/base).
