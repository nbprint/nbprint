build:
	jupyter nbconvert --to pdf sample.ipynb --template abc.tplx && open sample.pdf

tex:
	jupyter nbconvert --to latex sample.ipynb --template abc.tplx

clean:
	rm -rf *.tex sample_files/