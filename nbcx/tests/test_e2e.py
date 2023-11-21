from pprint import pprint

from nbconvert.nbconvertapp import main
from nbformat import write

from nbcx import generate, load


def test_e2e():
    config = load("examples/example.yaml")
    gen = generate(config)
    pprint(gen)
    with open("tmp.ipynb", "w") as fp:
        write(gen, fp)
    main(["tmp.ipynb", "--to=html", "--template=nbcx", "--execute"])
