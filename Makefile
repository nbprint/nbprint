build:
	jupyter nbconvert --to pdf sample.ipynb --template nbcx_templates/templates/abc.tplx && open sample.pdf

html:
	jupyter nbconvert --to html sample.ipynb --template nbcx_templates/templates/abc.tpl && open sample.html

tex:
	jupyter nbconvert --to latex sample.ipynb --template nbcx_templates/templates/abc.tplx

clean:
	rm -rf *.tex sample_files/ *.log *.aux *.synctex* 