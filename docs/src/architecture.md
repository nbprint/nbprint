# Architecture

`nbprint` is a collection of [`pydantic`](https://docs.pydantic.dev/latest/) models to take or construct a Jupyter notebook from
a set of standard parts, execute it with [`nbconvert`](https://nbconvert.readthedocs.io/en/latest/), and convert it to `html` or `pdf`
with a standard template optionally running [`pagedjs`](https://pagedjs.org) to provide a print-oriented layout.

It can be run off an existing notebook, or using the provided [YAML-based configuration framework](./configuration.md).

```mermaid
graph TB
    nb("notebook<br>(.ipynb)")
    nbc{nbconvert}
    nbct[/nbprint <br> template/]
    pjs[/paged.js <br> layout engine/]
    o@{ shape: doc, label: "output (html,pdf,etc)" }

    nb --->nbc
    %% nb e2@--->nbc
    %% e2@{animate: true}

    nbct --> nbc
    pjs --- nbct

    nbc -->o
    %% nbc e3@-->o
    %% e3@{animate: true}
```

## Components

`nbprint` provides a core `Configuration` object with parameters for controlling:

- `Parameters`: input parameters (like [papermill](https://github.com/nteract/papermill))
- `Outputs`: output assets, generally using `nbconvert` to create an `html` or `pdf` document
- `Page`: print-media specific page elements, like header/footer, page numbers, etc
- `Context`: a shared object instantiated in our notebook and passed to every content cell.
  This allows us to represent notebook "state" as a typed `pydantic` model.
- `Content`: a structured object representing the actual cells in our notebook

### `Configuration`

```mermaid
graph LR
    subgraph Configuration
    pfile@{ shape: doc, label: "Parameters file<br>(json,jsonl,CLI)" }
    paramyaml>yaml]
    param["Parameters"]
    configyaml> yaml]
    config["Configuration"]
    ctxyaml>yaml]
    ctx["Context"]
    pageyaml>yaml]
    page["Page"]
    cntyaml>yaml]
    cnt["Content"]
    nb@{ shape: doc, label: "Existing Notebook<br>(.ipynb)" }
    outyaml>yaml]
    out["Outputs"]
    end

    subgraph Notebook
    pcell(Parameters Cell)
    configcell(Configuration Cell)
    pagecell(Page Cell)
    ctxcell(Context Cell)
    contentcell("Content Cell/s")
    outputcell(Outputs Cell)
    end

    paramyaml---> param
    %% paramyaml eparamyamlparam@---> param
    %% eparamyamlparam@{animate: true}
    pfile --->param
    %% pfile epfileparam@--->param
    %% epfileparam@{animate: true}
    param --> config

    ctxyaml --> ctx
    %% ctxyaml ectxyamlctx@---> ctx
    %% ectxyamlctx@{animate: true}
    ctx --> config

    pageyaml --> page
    %% pageyaml epageyamlpage@---> page
    %% epageyamlpage@{animate: true}
    page --> config

    nb --->cnt
    %% nb enbcnt@--->cnt
    %% enbcnt@{animate: true}
    cntyaml ---> cnt
    %% cntyaml ecntyamlcnt@---> cnt
    %% ecntyamlcnt@{animate: true}
    cnt --> config

    outyaml ---> out
    %% outyaml eoutyamlout@---> out
    %% eoutyamlout@{animate: true}
    out --> config

    configyaml --> config
    %% configyaml econfigyamlconfig@---> config
    %% econfigyamlconfig@{animate: true}

    pcell---configcell
    configcell---pagecell
    pagecell---ctxcell
    ctxcell---contentcell
    contentcell --- outputcell

    subgraph Output
    o@{ shape: doc, label: "output (html,pdf,etc)" }
    end

    Configuration --> Notebook
    Notebook -->Output
```

### `Parameters`

Parameters are the first cell of a notebook, and can be passed in during execution to allow for parameterized notebooks.

We provide the following builtin versions:

#### `PapermillParameters`

> `hydra` config: `nbprint/parameters/papermill`

This is a basic object that takes any basic json-serializeable type and provides it in assignment as the first cell.

As an example, the following `YAML`:

```yaml
# @package nbprint.parameters
_target_: nbprint.PapermillParameterss
a: abc
b: 1.2
c: true
```

Would result in the following cell:

```python
a = "abc"
b = 1.2
c = True
```

### `Page`

### `Context`

### `Content`

### `Outputs`

`nbprint` can produce a variety of outputs based on [`nbconvert`](https://nbconvert.readthedocs.io/en/latest/).
It can also postprocess these outputs based on content, to e.g. email a report if a certain cell returns `True`, as a simple example.

The following defaults are provided:

#### `NBConvertOutputs`

> `hydra` config: `nbprint/outputs/default`

This `Outputs` runs `nbconvert` to produce an output document.
It supports the following configuration options:

- `target`: `nbconvert` target, in `html`, `pdf`, or `notebook`
- `execute`: whether or not to reexecute the notebook, defaults to `True`
- `timeout`: execution timeout, defaults to `600s`
- `template`: `nbconvert` template to use, defaults to `"nbprint"`

#### `PDFOutputs`

> `hydra` config: `nbprint/outputs/pdf`

Same as `NBConvertOutputs`, but with `target=pdf`.

#### `NotebookOutputs`

> `hydra` config: `nbprint/outputs/notebook`

Same as `NBConvertOutputs`, but with `target=notebook`.

#### `HTMLOutputs`

> `hydra` config: `nbprint/outputs/html`

Same as `NBConvertOutputs`, but with `target=html`.

#### `WebHTMLOutputs`

> `hydra` config: `nbprint/outputs/webhtml`

Same as `NBConvertOutputs`, but with `target=webhtml`.

#### `NBConvertShortCircuitOutputs`

A specialized `NBConvertOutputs` that stops output processing if a cell tagged `nbprint:output:stop` returns `True`

- `execute_hook`: A Python import path to a function to evaluate, see `nbprint.config.outputs.nbconvert.short_circuit_hook` as an example

## Configuration

[`hydra`](https://hydra.cc) allows us the ability to mix and match the various components defined in YAML, or even build our own.
Its easy for us to mix-and-match configuration for content, outputs, layout, and more.
It also lets us tweak existing `pydantic`-defined options from the command line.

Let's look at some examples of how powerful this can be:

In this command, we run a default `nbprint.Configuration` but use content from an existing notebook.

```bash
# Create HTML from notebook as-is
nbprint examples/basic.ipynb
```

In this command, we tweak the `nbprint.Configuration` object's `.name` attribute to be `"test"`, and we tweak the `nbprint.Configuration` object's `outputs` subobject's `.target` attribute to be `"pdf"`.

```bash
nbprint examples/basic.ipynb +nbprint.name=test ++nbprint.outputs.target=pdf

```

In this command, we tweak the `nbprint.Configuration` object's `parameters` subobject to add a new key `"a"` with value `"test"`.
This will inject the following first cell into our notebook:

```bash
# First cell is papermill-style parameters
nbprint examples/parameters.ipynb +nbprint.parameters.a=test
```

```python
a = "test"
```

This allows us to integrate nicely with [papermill](https://github.com/nteract/papermill) notebooks, and build parameterized reports to produce different outputs from the same skeleton notebook.

In this command, we take an existing notebook content and inject some content as frontmatter.

```bash
# Overlay a config group, e.g. title and table of contents
nbprint examples/basic.ipynb nbprint/content/frontmatter=nbprint/title_toc
```

In particular, we grab the code defined in `nbprint/config/hydra/content/frontmatter/nbprint/title_toc.yaml`:

```yaml
# @package nbprint.content.frontmatter
- _target_:  nbprint.ContentMarkdown
  content: |
    # ${nbprint.name}
  css: ":scope { text-align: center; }"
- _target_:  nbprint.ContentPageBreak
- _target_:  nbprint.ContentTableOfContents
- _target_:  nbprint.ContentPageBreak
```

Similar to the previous command, this command swaps `nbprint.Configuration` object's `outputs` subobject to be the
object defined in `nbprint/config/hydra/outputs/nbprint/pdf.yaml`:

```bash
# Create PDF via WebPDF by using hydra to swap out outputs type
nbprint examples/basic.ipynb nbprint/outputs=nbprint/pdf
```

That content just defines a different `nbprint.Outputs` object in `YAML`:

```yaml
# @package nbprint.outputs
_target_: nbprint.PDFOutputs
target: webpdf
```

Finally, we could accomplish the same thing by tweaking the default `Outputs` object's `.target` attribute to be `webpdf`.

```bash
# Create PDF via WebPDF same as above by using hydra to tweak the default output target
nbprint examples/basic.ipynb ++nbprint.outputs.target=webpdf
```

By providing the ability to do deep dependency injection in existing objects and/or swap objects wholesale,
we can customize, tweak, and extend `nbprint` as much as we need.
