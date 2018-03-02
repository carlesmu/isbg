# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS       = -a -E -n
SPHINXBUILD      = sphinx-build
SPHINXAPIDOC     = sphinx-apidoc
SPHINXAPIDOCOPTS = --force --separate --private --follow-links
SPHINXPROJ       = isbg
TMPDIR           = ../build.sphinx
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
	$(SPHINXAPIDOC) -o "$(TMPDIR)" "$(SOURCEPYDIR)" $(SPHINXAPIDOCOPTS)

clean-all:
	@rm -fr "$(BUILDDIR)"
	@rm -fr "$(TMPDIR)"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	mkdir -p "$(TMPDIR)"
	cp -f ../*.rst "$(TMPDIR)"
	cp -f ../*.md "$(TMPDIR)"
	cp -fr * "$(TMPDIR)"
	$(SPHINXBUILD) -M $@ "$(TMPDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
