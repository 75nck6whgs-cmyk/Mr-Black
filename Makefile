# Aviation Pipeline — Makefile
# Shortcuts for the most common operations.
# Usage: make build EP=episode_002.json
#        make upload EP=output/episode_002.mp4 TITLE="When Pilots Save the Day"
#        make batch
#        make setup

PYTHON   := .venv/bin/python3
PIP      := .venv/bin/pip
EP       ?= episode_002.json
TITLE    ?= $(shell $(PYTHON) -c "import json; print(json.load(open('$(EP)'))['title'])" 2>/dev/null || echo "Aviation Breakdown")
MODEL    ?= base
PRIVACY  ?= private

.PHONY: help setup build caption thumbnail upload batch clean

help:
	@echo ""
	@echo "  make setup                        Install dependencies (run once on server)"
	@echo "  make build    EP=episode_002.json Build + caption + thumbnail"
	@echo "  make batch                        Build all episodes in schedule.json"
	@echo "  make upload   EP=output/ep.mp4   Upload to YouTube (private by default)"
	@echo "  make clean                        Remove processed/ and output/ files"
	@echo ""
	@echo "  Options:"
	@echo "    EP=<manifest.json>              Episode manifest (default: episode_002.json)"
	@echo "    MODEL=small                     Whisper model size (tiny/base/small/medium/large)"
	@echo "    PRIVACY=public                  Upload privacy (private/unlisted/public)"
	@echo ""

setup:
	bash vps_setup.sh

venv:
	python3 -m venv .venv
	$(PIP) install --upgrade pip --quiet
	$(PIP) install -r requirements.txt --quiet
	@echo "✅ Virtualenv ready"

build: venv
	bash build.sh $(EP) --model=$(MODEL)

caption: venv
	$(PYTHON) caption_episode.py output/$(basename $(EP) .json).mp4 --model $(MODEL)

thumbnail: venv
	$(PYTHON) make_thumbnail.py output/$(basename $(EP) .json).mp4 "$(TITLE)"

upload: venv
	$(PYTHON) upload_episode.py output/$(basename $(EP) .json).mp4 \
		--title "$(TITLE)" \
		--privacy $(PRIVACY)

batch: venv
	$(PYTHON) batch_build.py schedule.json

clean:
	rm -f processed/*.mp4 output/*.mp4 output/*.txt
	@echo "Cleaned processed/ and output/"
