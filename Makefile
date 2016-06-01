
define HELP

This is the fdjangodog Makefile.

Usage:

make requirements - Install dependencies
make coverage     - Run coverage analysis
make lint         - Run static analysis
make test         - Run static analysis, tests with coverage
make quicktest    - Run tests without coverage
make cleantest    - Run tests cleaning tox environment first
make clean        - Remove generated files
endef

export HELP


.PHONY: all clean help lint quicktest requirements sdist test


all help:
	@echo "$$HELP"


requirements: .requirements.txt


.requirements.txt: requirements/*.txt
	pip install -r requirements/development.txt
	pip freeze > $@


lint: requirements
	flake8 c3pyo | tee c3pyo_lint.txt


quicktest: requirements
	tox


coverage: requirements
	tox -e coverage


test: coverage lint


clean:
	rm -rf .coverage coverage.xml coverage-report .requirements.txt fd_c3pyo.egg-info dist .tox testresults_*.xml
	find . -name '*.pyc' -delete


sdist: requirements
	python setup.py sdist
