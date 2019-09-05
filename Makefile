build:
	jupyter nbconvert --to pdf sample.ipynb --template nbcx_templates/templates/abc.tplx && open sample.pdf

tex:
	jupyter nbconvert --to latex sample.ipynb --template nbcx_templates/templates/abc.tplx

clean:
	rm -rf *.tex sample_files/ *.log *.aux *.synctex* 