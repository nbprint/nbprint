PYTHON=python3

build:
	jupyter nbconvert --to pdf sample.ipynb --template nbcx_templates/templates/abc.tplx && open sample.pdf

html:
	jupyter nbconvert --to html sample.ipynb --template nbcx_templates/templates/abc.tpl && open sample.html

tex:
	jupyter nbconvert --to latex sample.ipynb --template nbcx_templates/templates/abc.tplx

test: lint ## run the tests for travis CI
	@ ${PYTHON} -m pytest -v tests --cov=jupyterlab_templates

lint: ## run linter
	flake8 jupyterlab_templates 

clean: ## clean the repository
	find . -name "__pycache__" | xargs  rm -rf 
	find . -name "*.pyc" | xargs rm -rf 
	find . -name ".ipynb_checkpoints" | xargs  rm -rf 
	rm -rf .coverage cover htmlcov logs build dist *.egg-info lib node_modules

install:  ## install to site-packages
	${PYTHON} -m pip install .

fix:  ## run autopep8/tslint fix
	autopep8 --in-place -r -a -a crowdsource/

dist:  js  ## dist to pypi
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
