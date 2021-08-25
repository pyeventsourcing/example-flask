# if a .env file exists load it
# otherwise we are in the CI server variables are already set
-include .env

# directory to store virtual environment
VENV_NAME=venv

# python runtime version
PYTHON_VER=3.8

# python executable
PYTHON?=${VENV_NAME}/bin/python${PYTHON_VER}

.PHONY: help configure

help:			## Shows this message.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

configure:		## Install required debian packages.
configure:
	sudo apt-get -y install python${PYTHON_VER} python3-pip
	python3 -m pip install --upgrade pip
	python3 -m pip install virtualenv
	make venv

venv:			## Recreate the virtual environment.
venv: ${VENV_NAME}/bin/activate
${VENV_NAME}/bin/activate:
	test -d ${VENV_NAME} || virtualenv -p python${PYTHON_VER} ${VENV_NAME}
	${PYTHON} -m pip install -U pip
	touch $@

freeze:         ## Freeze python requirements
freeze:
	${VENV_NAME}/bin/pip freeze | grep -v pkg-resources==0.0.0 > requirements.txt

up:
	docker-compose up --build -d

down:
	docker-compose down

logs:
	docker-compose logs -f app
