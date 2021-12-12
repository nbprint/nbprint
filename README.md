# nbconvertX
A framework for customizing NBConvert templates and building reports

[![Build Status](https://github.com/timkpaine/nbcx/workflows/Build%20Status/badge.svg?branch=main)](https://github.com/timkpaine/nbcx/actions?query=workflow%3A%22Build+Status%22)
[![Coverage](https://codecov.io/gh/timkpaine/nbcx/branch/main/graph/badge.svg?token=ag2j2TV2wE)](https://codecov.io/gh/timkpaine/nbcx)
[![GitHub issues](https://img.shields.io/github/issues/timkpaine/nbcx.svg)]()
[![PyPI](https://img.shields.io/pypi/l/nbcx.svg)](https://pypi.python.org/pypi/nbcx)
[![PyPI](https://img.shields.io/pypi/v/nbcx.svg)](https://pypi.python.org/pypi/nbcx)

## Templates
NBConvert's default templates are largely designed with academic styling. This repo is a collection of templates with industrial/business reports in mind.

## Gallery

|||
|:--|:--|
|Sample - PDF||
|[![sample.pdf](examples/template1.png)](examples/template1.pdf)|[Template](nbconvert/templates/nbcx_template1_pdf/index.tex.j2)|


## Getting started
You can install via:

`pip install nbcx`

or from source:

`python setup.py install`


## Usage
This library exposes a variety of templates (See the gallery above), as well as a few exporters to handle customizations not possible with `nbconvert` exporters. Thus, we expose a number of targets (you can see these as `entrypoints` with `nbconvert.exporters` key in the `setup.py` file).

Here is an example usage:

`jupyter nbconvert --to nbcx_pdf sample.ipynb  --execute --template nbcx/templates/reports/abc.tex.j2`



