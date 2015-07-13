GSPATH = $(shell gs --help | tr ':' '\n' | tr ' ' '\n' | grep "ghostscript/.*/lib")
PDFOPTS = -dSAFER -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite \
	  -dCompatibilityLevel=1.4 -dPDFSETTINGS=/prepress \
	  -dMaxSubsetPct=100 -dSubsetFonts=true -dEmbedAllFonts=true \
	  -dMaxInlineImageSize=0 -dDetectDuplicateImage=true
PDFOPTS2 =

all: talk.pdf setting_up.pdf

clean:
	rm -f *~ *.pdf *.ps *.dvi *.log *.aux *.toc *.bak *.out *.vrb *.nav
	rm -f *.log *.aux *.toc *.tmp.pdf *.pdf.new *.tpm *.icc *.toc *.smn *.mf.*

# rule to produce thumbnails from a temporary pdf file
%.tpm: %.tmp.pdf
	thumbpdf --level2 --compress 9 --modes=dvips $<

# rule to produce a temporary pdf file from a tex file for thumbnails
%.tmp.pdf: %.tex
	rm -f $(patsubst %.tex,%.mf.*,$<)
	latex $<
	grep -q "\\citation" $(patsubst %.tex,%.aux,$<) && bibtex $(patsubst %.tex,%,$<) || true
	test -f $(patsubst %.tex,%-fmf.mp,$<) && mpost -interaction=batch $(patsubst %.tex,%-fmf.mp,$<) || true
	latex $<
	latex $<
	dvips -Ppdf -z -G0 $(patsubst %.tex,%.dvi,$<)
	gs $(PDFOPTS) -sOutputFile=$(patsubst %.tex,%.pdf,$<) -c .setpdfwrite $(PDFOPTS2) -f$(patsubst %.tex,%.ps,$<)
	pdfopt $(patsubst %.tex,%.pdf,$<) $(patsubst %.tex,%.tmp.pdf,$<)
	rm -f $(patsubst %.tex,%.dvi,$<) $(patsubst %.tex,%.ps,$<) $(patsubst %.tex,%.pdf,$<)

# rule how to make a dvi from a tex file and its thumbnails
%.dvi: %.tex
	make $(patsubst %.tex,%.tpm,$<)
	latex $<
	grep -q "\\citation" $(patsubst %.tex,%.aux,$<) && bibtex $(patsubst %.tex,%,$<) || true
	latex $<
	latex $<

# rule how to make a ps file from a dvi
%.ps: %.dvi
	dvips -Ppdf -z -G0 $<

# rule how to make a pdf from a ps file
%.pdf: %.ps
	gs $(PDFOPTS) -sOutputFile=$(patsubst %.ps,%.pdf,$<) -c .setpdfwrite $(PDFOPTS2) -f$<
	pdfopt $(patsubst %.ps,%.pdf,$<) $(patsubst %.ps,%.pdf.new,$<)
	mv $(patsubst %.ps,%.pdf.new,$<) $(patsubst %.ps,%.pdf,$<)

%.djvu: %.pdf
	pdf2djvu -d 600 -o $(patsubst %.pdf,%.djvu,$<) $< || \
	    ( pdftops -level3 $< $<.tmp.ps; ps2pdf14 $<.tmp.ps; \
	    pdf2djvu -d 600 -o $(patsubst %.pdf,%.djvu,$<) $<.tmp.pdf); rm -f $<.tmp.{ps,pdf}

fixme:
	grep "FIXME" *.tex

spellcheck:
	for i in *.tex; do aspell -c -d en_GB-ise -t $$i; done

# create an icc file (might one day be useful for PDF/A creation)
icc:
	echo "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"\
	    "QkSMyAcAAA==" | tr ' ' '\n' | base64 -d | gunzip - | dd of=ISO\ Coated\ sb.icc
