.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep


.PHONY: show
show:             ## Show the current environment.
	@echo "Current environment:"
	poetry env info

.PHONY: install
install:          ## Install the project in dev mode.
	poetry install

.PHONY: fmt
fmt:              ## Format code using black & isort.
	isort simple_maps/
	black -l 79 simple_maps/
	black -l 79 tests/

.PHONY: lint
lint:             ## Run pep8, black, mypy linters.
	flake8 simple_maps/
	black -l 79 --check simple_maps/
	black -l 79 --check tests/
	mypy --ignore-missing-imports simple_maps/

.PHONY: test
test: lint        ## Run tests and generate coverage report.
	pytest -v --cov-config .coveragerc --cov=simple_maps -l --tb=short --maxfail=1 tests/
	coverage xml
	coverage html

.PHONY: watch
watch:            ## Run tests on every change.
	ls **/**.py | entr pytest -s -vvv -l --tb=long --maxfail=1 tests/

.PHONY: clean
clean:            ## Clean unused files.
	@find ./ -name '*.pyc' -exec rm -f {} \;
	@find ./ -name '__pycache__' -exec rm -rf {} \;
	@find ./ -name 'Thumbs.db' -exec rm -f {} \;
	@find ./ -name '*~' -exec rm -f {} \;
	@rm -rf .cache
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -rf htmlcov
	@rm -rf .tox/
	@rm -rf docs/_build

.PHONY: virtualenv
virtualenv:       ## Create a virtual environment.
	poetry install

.PHONY: release
release:          ## Create a new tag for release.
	@echo "WARNING: This operation will create s version tag and push to github"
	@read -p "Version? (provide the next x.y.z semver) : " TAG
	@echo "creating git tag : $${TAG}"
	@git tag $${TAG}
	@echo "$${TAG}" > simple_maps/VERSION
	@gitchangelog > HISTORY.md
	@git add simple_maps/VERSION HISTORY.md
	@git commit -m "release: version $${TAG} 🚀"
	@git push -u origin HEAD --tags
	@echo "Github Actions will detect the new tag and release the new version."

.PHONY: docs
docs:             ## Build the documentation.
	@echo "building documentation ..."
	@mkdocs build
	URL="site/index.html"; xdg-open $$URL || sensible-browser $$URL || x-www-browser $$URL || gnome-open $$URL

# Thanks to @rochacbruno
