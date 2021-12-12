TEMPLATE=1

buildtpl:  ## build a sample pdf report
	NBCX_CONTEXT=pdf jupyter nbconvert --to nbcx_pdf example_notebooks/template${TEMPLATE}.ipynb  --execute --template nbcx_template${TEMPLATE}_pdf && open example_notebooks/template${TEMPLATE}.pdf

html:  ## build a sample html report
	NBCX_CONTEXT=html jupyter nbconvert --to nbcx_html example_notebooks/template${TEMPLATE}.ipynb  --execute --template nbcx_template${TEMPLATE}_html && /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome example_notebooks/template${TEMPLATE}.html

tex:  ## build a sample latext report
	NBCX_CONTEXT=pdf jupyter nbconvert --to nbcx_latex example_notebooks/template${TEMPLATE}.ipynb --execute --template nbcx_template${TEMPLATE}_pdf && code example_notebooks/template${TEMPLATE}.tex

build1:  ## build pdf first template
	make buildtpl TEMPLATE=1 

html1:  ## build html first template
	make html TEMPLATE=1 

tex1:  ## build tex first template
	make tex TEMPLATE=1 

build2:  ## build pdf first template
	make buildtpl TEMPLATE=2

html2:  ## build html first template
	make html TEMPLATE=2

tex2:  ## build tex first template
	make tex TEMPLATE=2

build: ## build python
	python setup.py build

tests: lint ## run the tests
	python -m pytest -vv nbcx/tests --cov=nbcx --junitxml=python_junit.xml --cov-report=xml --cov-branch

lint: ## run linter
	python -m flake8 nbcx setup.py docs/conf.py

fix:  ## run black fix
	python -m black nbcx/ setup.py docs/conf.py

clean: ## clean the repository
	find . -name "__pycache__" | xargs  rm -rf 
	find . -name "*.pyc" | xargs rm -rf 
	find . -name ".ipynb_checkpoints" | xargs  rm -rf 
	rm -rf .coverage cover htmlcov logs build dist *.egg-info lib node_modules .pytest_cache coverage.xml python_junit.xml docs/nbcx docs/examples .pytest_cache .coverage coverage.xml sample_files sample.out sample.tex
	git clean -fd
	rm -rf *.fdb_latexmk *.aux *.fls *.log *.pdf *.synctex*
	make -C ./docs clean

docs:  ## make documentation
	make -C ./docs html
	open ./docs/_build/html/index.html

install:  ## install to site-packages
	python -m pip install .

dist:  ## create dists
	rm -rf dist build
	python setup.py sdist bdist_wheel
	python -m twine check dist/*
	
publish: dist  ## dist to pypi
	python -m twine upload dist/* --skip-existing

# Thanks to Francoise at marmelab.com for this
.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

print-%:
	@echo '$*=$($*)'

.PHONY: clean install serverextension labextension test tests help docs dist build build1 build2 tex tex1 tex2 html html1 html2
