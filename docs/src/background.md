# Background

Jupyter Notebooks are widely used for reports via [`nbconvert`](https://nbconvert.readthedocs.io/en/latest/). Most efforts focus on building web reports / websites from notebooks, including [`Voilà`](https://github.com/voila-dashboards/voila) and [`Jupyter Book`](https://jupyterbook.org/en/stable/intro.html).

Despite being the primary goal of early notebook conversion efforts, in recent years much less focus has been spent on print media - PDFs for reports, academic papers, newspapers, etc. There are many examples of `nbconvert` templates for academic papers, as well as projects like [`ipypublish`](https://github.com/chrisjsewell/ipypublish/tree/develop). Most of these efforts focus on $\\LaTeX$, and indeed `nbprint` itself started as convenience framework for formatting charts and tables similarly between html and pdf outputs.

However, with recent releases to `nbconvert`, which now supports `webpdf` (printing as pdf from within a headless web browser), and with advances to the `@media print` CSS directive spearheaded by the lovely folks at [`pagedjs`](https://pagedjs.org), it is now much easier to build publication ready print-oriented media on the web.

This is the goal of `nbprint`. Using [`pagedjs`](https://pagedjs.org), `nbprint` provides templates and utilities for building web reports targeting print media. Beyond that, it provides infrastructure for parameterizing and configuring documents via [`pydantic`](https://docs.pydantic.dev/latest/), which makes designing and generating reports a breeze, even without knowledge of Python. Documents are modular and can be easily composed via [`hydra`](https://hydra.cc).

## Related Projects

- [`nbconvert`](https://nbconvert.readthedocs.io/en/latest/): Convert Notebooks to other formats
- [`pagedjs`](https://pagedjs.org): Paged.js is a free and open-source library that paginates any HTML content to produce beautiful print-ready PDF
- [`Voilà`](https://github.com/voila-dashboards/voila): Voilà turns Jupyter notebooks into standalone web applications
- [Jupyter Book](https://jupyterbook.org/en/stable/intro.html): Build beautiful, publication-quality books and documents from computational content
- [`ipypublish`](https://github.com/chrisjsewell/ipypublish/tree/develop): A workflow for creating and editing publication ready scientific reports and presentations, from one or more Jupyter Notebooks, without leaving the browser!

Additionally, this project relies heavily on:

- [`pydantic`](https://docs.pydantic.dev/latest/): Pydantic is the most widely used data validation library for Python.
- [`hydra`](https://hydra.cc): Hydra is a framework for dynamically creating hierarchical configuration by composition, with the ability to override through config files and the command line
- [`omegaconf`](https://github.com/omry/omegaconf): OmegaConf is a hierarchical configuration system, with support for merging configurations from multiple sources
- [`typer`](https://typer.tiangolo.com): Typer is a library for building CLI applications based on Python type hints
