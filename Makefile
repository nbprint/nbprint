PYTHON=python3.7

build:  ## build a sample pdf report
	jupyter nbconvert --to pdf sample.ipynb --template nbcx_templates/templates/reports/abc.tplx && open sample.pdf

html:  ## build a sample html report
	jupyter nbconvert --to html sample.ipynb --template nbcx_templates/templates/reports/abc.tpl && open sample.html

tex:  ## build a sample latext report
	jupyter nbconvert --to latex sample.ipynb --template nbcx_templates/templates/reports/abc.tplx

tests: lint ## run the tests
	${PYTHON} -m pytest -v nbcx_templates/tests --cov=nbcx_templates --junitxml=python_junit.xml --cov-report=xml --cov-branch

lint: ## run linter
	flake8 jupyterlab_templates 

clean: ## clean the repository
	find . -name "__pycache__" | xargs  rm -rf 
	find . -name "*.pyc" | xargs rm -rf 
	find . -name ".ipynb_checkpoints" | xargs  rm -rf 
	rm -rf .coverage cover htmlcov logs build dist *.egg-info lib node_modules
	git clean -fd
	make -C ./docs clean

docs:  ## make documentation
	make -C ./docs html
	open ./docs/_build/html/index.html

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
