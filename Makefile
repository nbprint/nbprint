PYTHON=python3.7

build:  ## build a sample pdf report
	NBCX_CONTEXT=pdf jupyter nbconvert --to nbcx_pdf sample.ipynb  --execute --template nbcx/templates/reports/abc.tex.j2 && open sample.pdf

html:  ## build a sample html report
	NBCX_CONTEXT=html jupyter nbconvert --to html sample.ipynb  --execute --template nbcx/templates/reports/abc.html.j2 && open sample.html

tex:  ## build a sample latext report
	NBCX_CONTEXT=pdf jupyter nbconvert --to nbcx_latex sample.ipynb --execute --template nbcx/templates/reports/abc.tex.j2 && code sample.tex

tests: lint ## run the tests
	${PYTHON} -m pytest -v nbcx/tests --cov=nbcx --junitxml=python_junit.xml --cov-report=xml --cov-branch

lint: ## run linter
	python3.7 -m flake8 nbcx 

clean: ## clean the repository
	find . -name "__pycache__" | xargs  rm -rf 
	find . -name "*.pyc" | xargs rm -rf 
	find . -name ".ipynb_checkpoints" | xargs  rm -rf 
	rm -rf .coverage cover htmlcov logs build dist *.egg-info lib node_modules .pytest_cache coverage.xml python_junit.xml docs/nbcx docs/examples .pytest_cache .coverage coverage.xml sample_files sample.out sample.tex
	git clean -fd
	make -C ./docs clean

docs:  ## make documentation
	make -C ./docs html
	open ./docs/_build/html/index.html

install:  ## install to site-packages
	${PYTHON} -m pip install .

fix:  ## run autopep8/tslint fix
	python3.7 -m autopep8 --in-place -r -a -a nbcx/

dist:  ## dist to pypi
	rm -rf dist build
	${PYTHON} setup.py sdist
	${PYTHON} setup.py bdist_wheel
	twine check dist/* && twine upload dist/*

# Thanks to Francoise at marmelab.com for this
.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

print-%:
	@echo '$*=$($*)'

.PHONY: clean install serverextension labextension test tests help docs dist
