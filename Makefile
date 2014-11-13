BUNDLE       = BD-TP2.tar.gz
BUNDLE_DIR   = BD-TP2
BUNDLE_FILES = source tex Makefile README.md enunciado.pdf informe.pdf

.PHONY: all informe.pdf custom-dataset plots plot-custom-datasets \
	      plot-performance plot-datasets clean clean-tex bundle

all: plots informe.pdf

informe.pdf:
	make -C tex all
	mv tex/informe.pdf .

custom-dataset:
	cd source; ./generate-custom-datasets.py

plots: plot-custom-datasets plot-performance plot-datasets

plot-custom-datasets:
	cd source; ./plot-custom-datasets.py

plot-performance:
	cd source; ./plot-performance.py --hist-uniform-equal   -o ../tex/plot-hist-uniform-equal.pdf
	cd source; ./plot-performance.py --hist-uniform-greater -o ../tex/plot-hist-uniform-greater.pdf
	cd source; ./plot-performance.py --hist-normal-equal    -o ../tex/plot-hist-normal-equal.pdf
	cd source; ./plot-performance.py --hist-normal-greater  -o ../tex/plot-hist-normal-greater.pdf

	cd source; ./plot-performance.py --diststep-uniform-equal   -o ../tex/plot-diststep-uniform-equal.pdf
	cd source; ./plot-performance.py --diststep-uniform-greater -o ../tex/plot-diststep-uniform-greater.pdf
	cd source; ./plot-performance.py --diststep-normal-equal    -o ../tex/plot-diststep-normal-equal.pdf
	cd source; ./plot-performance.py --diststep-normal-greater  -o ../tex/plot-diststep-normal-greater.pdf

	cd source; ./plot-performance.py --custom-uniform-equal   -o ../tex/plot-custom-uniform-equal.pdf
	cd source; ./plot-performance.py --custom-uniform-greater -o ../tex/plot-custom-uniform-greater.pdf
	cd source; ./plot-performance.py --custom-normal-equal    -o ../tex/plot-custom-normal-equal.pdf
	cd source; ./plot-performance.py --custom-normal-greater  -o ../tex/plot-custom-normal-greater.pdf

plot-datasets:
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
