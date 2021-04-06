.DELETE_ON_ERROR:
.ONESHELL:
.SHELLFLAGS   := -eu -o pipefail -c
.SILENT:
MAKEFLAGS     += --no-builtin-rules
MAKEFLAGS     += --warn-undefined-variables
SHELL         = bash

DEBUG        = TOMATE_DEBUG=1
DOCKER_IMAGE = eliostvs/tomate
OBS_API_URL  = https://api.opensuse.org:443/trigger/runservice
PLUGINPATH   = $(CURDIR)/data/plugins
PYTHONPATH   = PYTHONPATH=$(CURDIR)/tomate:$(PLUGINPATH)
VERSION      = `cat .bumpversion.cfg | grep current_version | awk '{print $$3}'`
WORKDIR      = /code
XDGPATH      = XDG_DATA_HOME=$(CURDIR)/data

ifeq ($(origin .RECIPEPREFIX), undefined)
	$(error This Make does not support .RECIPEPREFIX. Please use GNU Make 4.0 or later)
endif

.PHONY: format
format:
	black data/plugins/ tests

.PHONY: clean
clean:
	find . \( -iname "*.pyc" -o -iname "__pycache__" -o -iname ".coverage" -o -iname ".cache" \) -print0 | xargs -0 rm -rf

.PHONY: submodule
submodule:
	git submodule init
	git submodule update

.PHONY: test
test: clean
	echo "$(DEBUG) $(XDGPATH) $(PYTHONPATH) $(ARGS) py.test $(PYTEST) --cov=$(PLUGINPATH)"
	$(DEBUG) $(XDGPATH) $(PYTHONPATH) $(ARGS) py.test $(PYTEST) --cov=$(PLUGINPATH)

release-%:
	git flow init -d
	@grep -q '\[Unreleased\]' CHANGELOG.md || (echo 'Create the [Unreleased] section in the changelog first!' && exit)
	bumpversion --verbose --commit $*
	git flow release start $(VERSION)
	GIT_MERGE_AUTOEDIT=no git flow release finish -m "Merge branch release/$(VERSION)" -T $(VERSION) $(VERSION)

.PHONY: trigger-build
trigger-build:
	curl -X POST -H "Authorization: Token $(TOKEN)" $(OBS_API_URL)

.PHONY: docker-clean
docker-clean:
	docker rmi $(DOCKER_IMAGE) 2> /dev/null || echo $(DOCKER_IMAGE) not found!

PHONY: docker-pull
docker-pull:
	docker pull $(DOCKER_IMAGE)

.PHONY: docker-test
docker-test:
	docker run --rm -v $(CURDIR):$(WORKDIR) --workdir $(WORKDIR) $(DOCKER_IMAGE)

.PHONY: docker-all
docker-all: docker-clean docker-pull docker-test

.PHONY: docker-enter
docker-enter:
	docker run --rm -v $(CURDIR):$(WORKDIR) --workdir $(WORKDIR) -it --entrypoint="bash" $(DOCKER_IMAGE)
