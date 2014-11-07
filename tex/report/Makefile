all: report

report: report.tex
	xelatex report.tex
#	gs -sDEVICE=pdfwrite -dNOPAUSE -dQUIET -dBATCH -dFirstPage=2 -sOutputFile=first2.pdf first.pdf

clean:
	rm -f *.log *.out *.dvi *toc