import os
from codecs import open
from os import path

from jupyter_packaging import get_version
from setuptools import find_packages, setup

pjoin = path.join

name = "nbcx"
here = path.abspath(path.dirname(__file__))
version = get_version(pjoin(here, name, "_version.py"))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

requires = [
    "dominate>=2.5.1",
    "IPython>=7.13.0",
    "ipywidgets>=7.5.1",
    "jupyter_client>=6.1.3",
    "nbconvert>=6.0.0a1",
    "pandas>=0.17.1",
    "testpath",
]

requires_dev = requires + [
    "black>=20.",
    "bump2version>=1.0.0",
    "flake8>=3.7.8",
    "flake8-black>=0.2.1",
    "mock",
    "pytest>=4.3.0",
    "pytest-cov>=2.6.1",
    "pytest-rerunfailures>=10.1",
    "recommonmark",
    "Sphinx>=1.8.4",
    "sphinx-markdown-builder>=0.5.2",
    "sphinx-rtd-theme",
]


def get_data_files():
    # Add all the templates
    data_files = []
    for (dirpath, dirnames, filenames) in os.walk("share/jupyter/nbconvert/templates/"):
        if filenames:
            data_files.append(
                (dirpath, [os.path.join(dirpath, filename) for filename in filenames])
            )
    return data_files


setup(
    name=name,
    version=version,
    description="NBConvert Templates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/timkpaine/nbcx",
    author="Tim Paine",
    author_email="t.paine154@gmail.com",
    license="Apache 2.0",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Framework :: Jupyter",
    ],
    keywords="jupyter nbconvert",
    packages=find_packages(
        exclude=[
            "tests",
        ]
    ),
    install_requires=requires,
    extras_require={"dev": requires + requires_dev},
    entry_points={
        "nbconvert.exporters": [
            "nbcx_html = nbcx.exporters:NBCXHTMLExporter",
            "nbcx_latex = nbcx.exporters:NBCXLatexExporter",
            "nbcx_pdf = nbcx.exporters:NBCXPDFExporter",
        ],
    },
    data_files=get_data_files(),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
)
