.PHONY: install data core map verify lab

install:
	python -m pip install -r requirements.txt

data:
	python scripts/download_data.py --all

core:
	python scripts/download_data.py --core

map:
	python scripts/download_data.py --map

verify:
	python scripts/verify_data.py

lab:
	jupyter lab
