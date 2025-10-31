NAME=cv
GENERATED_NAME=cv_generated

all: generated
	latexmk -pdf ${NAME}.tex

generate:
	python3 generate_cv.py

generated: generate
	latexmk -pdf ${GENERATED_NAME}.tex

clean:
	rm -f ${NAME}.aux ${NAME}.bbl ${NAME}.bcf ${NAME}.fdb_latexmk ${NAME}.fls ${NAME}.log ${NAME}.out ${NAME}.run.xml ${NAME}.blg ${NAME}.toc *\~
	rm -f ${GENERATED_NAME}.aux ${GENERATED_NAME}.bbl ${GENERATED_NAME}.bcf ${GENERATED_NAME}.fdb_latexmk ${GENERATED_NAME}.fls ${GENERATED_NAME}.log ${GENERATED_NAME}.out ${GENERATED_NAME}.run.xml ${GENERATED_NAME}.blg ${GENERATED_NAME}.toc

distclean: clean
	rm -f ${NAME}.pdf ${GENERATED_NAME}.pdf ${GENERATED_NAME}.tex

install-deps:
	pip3 install pyyaml

help:
	@echo "Available targets:"
	@echo "  all        - Generate CV from YAML and compile original cv.tex"
	@echo "  generate   - Generate cv_generated.tex from portfolio.yaml"
	@echo "  generated  - Generate and compile cv_generated.tex"
	@echo "  clean      - Remove temporary files"
	@echo "  distclean  - Remove all generated files including PDFs"
	@echo "  install-deps - Install Python dependencies"
