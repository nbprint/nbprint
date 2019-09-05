build:
	jupyter nbconvert --to pdf sample.ipynb --template abc.tplx && open sample.pdf

clean:
	rm -rf *.tex sample_files/