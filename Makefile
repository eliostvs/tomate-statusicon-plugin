PACKAGE = tomate-statusicon-plugin
AUTHOR = eliostvs
PACKAGE_ROOT = $(CURDIR)
TOMATE_PATH = $(PACKAGE_ROOT)/tomate
DATA_PATH = $(PACKAGE_ROOT)/data
PLUGIN_PATH = $(DATA_PATH)/plugins
XDG_DATA_DIRS = XDG_DATA_DIRS=$(DATA_PATH)
DOCKER_IMAGE_NAME = $(AUTHOR)/$(PACKAGE)
PYTHONPATH = PYTHONPATH=$(TOMATE_PATH):$(PLUGIN_PATH)
PROJECT = home:eliostvs:tomate
OBS_API_URL = https://api.opensuse.org:443/trigger/runservice?project=$(PROJECT)&package=$(PACKAGE)

submodule:
	git submodule init
	git submodule update

clean:
	find . \( -iname "*.pyc" -o -iname "__pycache__" \) -print0 | xargs -0 rm -rf

test: clean
	$(PYTHONPATH) py.test test.py --cov-report term-missing --cov=$(PLUGIN_PATH) -v --flake8

docker-clean:
	docker rmi $(DOCKER_IMAGE_NAME) 2> /dev/null || echo $(DOCKER_IMAGE_NAME) not found!

docker-build:
	docker build -t $(DOCKER_IMAGE_NAME) .
	
docker-test:
	docker run --rm -v $(PACKAGE_ROOT):/code $(DOCKER_IMAGE_NAME)

docker-all: docker-clean docker-build docker-test

docker-enter:
	docker run --rm -v $(PACKAGE_ROOT):/code -it --entrypoint="bash" $(DOCKER_IMAGE_NAME)

trigger-build:
	curl -X POST -H "Authorization: Token $(TOKEN)" $(OBS_API_URL)
