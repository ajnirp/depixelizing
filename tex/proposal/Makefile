all: proposal

proposal: proposal.tex
	xelatex proposal.tex
#	gs -sDEVICE=pdfwrite -dNOPAUSE -dQUIET -dBATCH -dFirstPage=2 -sOutputFile=first2.pdf first.pdf

clean:
	rm -f *.log *.out *.dvi *toc