PACKAGE = tomate-statusicon-plugin
AUTHOR = eliostvs
PACKAGE_ROOT = $(CURDIR)
TOMATE_PATH = $(PACKAGE_ROOT)/tomate
DATA_PATH = $(PACKAGE_ROOT)/data
PLUGIN_PATH = $(DATA_PATH)/plugins
XDG_DATA_DIRS = XDG_DATA_DIRS=$(DATA_PATH)
DOCKER_IMAGE_NAME = $(AUTHOR)/tomate
PYTHONPATH = PYTHONPATH=$(TOMATE_PATH):$(PLUGIN_PATH)
PROJECT = home:eliostvs:tomate
OBS_API_URL = https://api.opensuse.org/trigger/runservice
CURRENT_VERSION = `cat .bumpversion.cfg | grep current_version | awk '{print $$3}'`
DEBUG = TOMATE_DEBUG=true
WORK_DIR = /code

clean:
	find . \( -iname "*.pyc" -o -iname "__pycache__" \) -print0 | xargs -0 rm -rf

submodule:
	git submodule init;
	git submodule update;

test: clean
	$(PYTHONPATH) $(DEBUG) py.test test_plugin.py --cov=$(PLUGIN_PATH)

docker-clean:
	docker rmi $(DOCKER_IMAGE_NAME) 2> /dev/null || echo $(DOCKER_IMAGE_NAME) not found!

docker-pull:
	docker pull $(DOCKER_IMAGE_NAME)

docker-test:
	docker run --rm -v $(PACKAGE_ROOT):$(WORK_DIR) --workdir $(WORK_DIR) $(DOCKER_IMAGE_NAME)

docker-all: docker-clean docker-pull docker-test

docker-enter:
	docker run --rm -v $(PACKAGE_ROOT):$(WORK_DIR) --workdir $(WORK_DIR) -it --entrypoint="bash" $(DOCKER_IMAGE_NAME)

release-%:
	git flow init -d
	@grep -q '\[Unreleased\]' README.md || (echo 'Create the [Unreleased] section in the changelog first!' && exit)
	bumpversion --verbose --commit $*
	git flow release start $(CURRENT_VERSION)
	GIT_MERGE_AUTOEDIT=no git flow release finish -m "Merge branch release/$(CURRENT_VERSION)" -T $(CURRENT_VERSION) $(CURRENT_VERSION)

trigger-build:
	curl -X POST -H "Authorization: Token $(TOKEN)" $(OBS_API_URL)
