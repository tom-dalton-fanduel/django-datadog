
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


.requirements.txt: setup.py requirements/*.txt
	pip install -r requirements/development.txt
	pip freeze > $@


lint: requirements
	flake8 fdjangodog | tee fdjangodog_lint.txt


quicktest: requirements
	tox


coverage: requirements
	tox


test: coverage lint


clean:
	rm -rf .coverage coverage.xml coverage-report .requirements.txt fdjangodog.egg-info dist .tox testresults_*.xml
	find . -name '*.pyc' -delete


sdist: requirements
	python setup.py sdist


uploadtest:
	python setup.py sdist upload -r pypitest


upload:
	python setup.py sdist upload -r pypi
	