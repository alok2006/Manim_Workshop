# Manim Workshop — developer entry points.
#
# `make` on its own prints the list of targets.
# Everything runs through the virtual environment in .venv (see `make install`).

SHELL := /bin/bash
PYTHON ?= .venv/bin/python
QUALITY ?= l
JOBS ?= 6

.DEFAULT_GOAL := help

.PHONY: help venv install check dry-run render videos gallery test lint notebook clean

help:  ## Show this list
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

venv:  ## Create the virtual environment (.venv)
	python3 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip

install: venv  ## Install dependencies and the package (editable)
	$(PYTHON) -m pip install -r requirements-dev.txt
	$(PYTHON) -m pip install -e .

check:  ## Static checks on every scene (fast, renders nothing)
	$(PYTHON) scripts/check_scenes.py

dry-run:  ## Execute every scene without writing video (the real compile check)
	$(PYTHON) scripts/check_scenes.py --dry-run --jobs $(JOBS)

render:  ## Render every scene at QUALITY (default: l)
	$(PYTHON) scripts/check_scenes.py --render --quality $(QUALITY) --jobs $(JOBS)

videos:  ## Render and publish the committed previews into videos/
	$(PYTHON) scripts/check_scenes.py --render --quality l --jobs $(JOBS) --publish videos

gallery:  ## Regenerate the stills in docs/gallery/ from rendered videos
	$(PYTHON) scripts/make_gallery.py

scenes:  ## List every scene with its render command
	$(PYTHON) scripts/check_scenes.py --list

test:  ## Run the test-suite (one test renders a real video)
	$(PYTHON) -m pytest

lint:  ## Lint the Python sources with ruff
	$(PYTHON) -m ruff check .

notebook:  ## Open the workshop notebook in JupyterLab
	$(PYTHON) -m jupyterlab notebooks/workshop.ipynb

clean:  ## Move render output (media/) aside — never deletes it
	@if [ -d media ]; then \
		mkdir -p .trash && \
		mv media ".trash/media-$$(date +%Y%m%d-%H%M%S)" && \
		echo "moved media/ into .trash/ (nothing is ever deleted here)"; \
	else \
		echo "nothing to move: media/ does not exist"; \
	fi
