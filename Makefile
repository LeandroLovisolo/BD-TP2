BUNDLE       = BD-TP2.tar.gz
BUNDLE_DIR   = BD-TP2
BUNDLE_FILES = tex Makefile README.md enunciado.pdf informe.pdf

.PHONY: all informe.pdf plots clean clean-tex bundle

all: plots informe.pdf

informe.pdf:
	make -C tex all
	mv tex/informe.pdf .

plots:
	cd source; ./plot-datasets.py

bundle: clean informe.pdf
	make clean-tex
	mkdir $(BUNDLE_DIR)
	cp $(BUNDLE_FILES) $(BUNDLE_DIR) -r
	tar zcf $(BUNDLE) $(BUNDLE_DIR)
	rm -rf $(BUNDLE_DIR)

clean: clean-tex
	rm -rf informe.pdf $(BUNDLE) $(BUNDLE_DIR)

clean-tex:
	make -C tex clean
