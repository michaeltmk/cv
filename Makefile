NAME=cv

all: generate
	latexmk -pdf ${NAME}.tex

generate:
	python3 generate_cv.py

clean:
	rm -f ${NAME}.aux ${NAME}.bbl ${NAME}.bcf ${NAME}.fdb_latexmk ${NAME}.fls ${NAME}.log ${NAME}.out ${NAME}.run.xml ${NAME}.blg ${NAME}.toc *\~

distclean: clean
	rm -f ${NAME}.pdf ${NAME}.tex

install-deps:
	pip3 install pyyaml

help:
	@echo "Available targets:"
	@echo "  all        - Generate CV from YAML and compile to PDF"
	@echo "  generate   - Generate cv.tex from portfolio.yaml"
	@echo "  clean      - Remove temporary files"
	@echo "  distclean  - Remove all generated files including PDFs"
	@echo "  install-deps - Install Python dependencies"
