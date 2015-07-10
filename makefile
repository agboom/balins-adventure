mkenv:
	pyvenv-3.4 .virtualenv

install:
	test -d .virtualenv || ${MAKE} mkenv
	. .virtualenv/bin/activate; pip install -r requirements

test:
	. .virtualenv/bin/activate; cd src && python manage.py test

travis-install:
	pip install -r requirements

travis-test:
	cd src && python manage.py test
