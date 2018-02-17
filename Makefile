#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

# Note: required utilities:
# - For test: pytest
# - For cov: coverage
# - For tox: tox
# - For docs: sphinx and recommonmark
TEST   = pytest
COV    = ~/.local/bin/coverage
COVDIR = build/htmlcov
TOX    = tox

.PHONY: help all test-clean test cov-clean cov tox-clean tox docs clean \
        distclean apidoc

help:
	@echo "Please use 'make <target>' where target is one of:"
	@echo "  help       to show this help message."
	@echo "   "
	@echo "  test       to run the tests."
	@echo "  tox        to run tests with 'tox'."
	@echo "  cov        to check test 'coverage'."
	@echo "   "
	@echo "  docs       build the docs with 'sphinx'."
	@echo "   "
	@echo "  clean      clean generates files."
	@echo "  distclean  clean all generates files."


all: help


test-clean:
	rm -fr .pytest_cache

test:
	@$(TEST)

cov-clean:
	rm -f .coverage
	rm -fr $(COVDIR)

cov:
	@$(COV) run -m $(TEST)
	@$(COV) html --directory $(COVDIR)

tox-clean:
	rm -fr .tox

tox:
	@$(TOX)

apidoc: 
	$(MAKE) -C docs apidoc

html:
	$(MAKE) -C docs html

docs-clean:
	$(MAKE) -C docs clean

docs: apidoc html

clean: test-clean
	find . -name '*.pyc' -exec rm -f {} +
	rm -fr isbg/__pycache__
	rm -fr tests/__pycache__

distclean: clean tox-clean cov-clean docs-clean
	$(MAKE) -C docs clean-all
	rm -fr build
	rm -fr dist
	rm -fr sdist
	rm -fr isbg.egg-info
