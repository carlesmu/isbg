# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS       = -a -E -n
SPHINXBUILD      = sphinx-build
SPHINXAPIDOC     = sphinx-apidoc
SPHINXAPIDOCOPTS = --force --separate --private --follow-links
SPHINXPROJ       = isbg
SOURCEDIR        = .
BUILDDIR         = ../build/sphinx
SOURCEPYDIR      = ../isbg

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
	@echo " "
	@echo "  apidoc      to run $(SPHINXAPIDOC)"
	@echo "  clean-all   to clean all generated files"

.PHONY: help Makefile apidoc

# Creates the apidoc
apidoc:
	$(SPHINXAPIDOC) -o "$(SOURCEDIR)" "$(SOURCEPYDIR)" $(SPHINXAPIDOCOPTS)

clean-all:
	@rm -fr $(BUILDDIR)
	@rm *.rst
	@rm *.md

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@cp -f ../*.rst .
	@cp -f ../*.md .
	@cp -f src/*.rst .
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
