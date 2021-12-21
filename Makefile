export SHELL:=/bin/bash
.ONESHELL:
UNAME:=$(shell uname)

# ~~~~~ Setup Conda ~~~~~ #
# this sets the system PATH to ensure we are using in included 'conda' installation for all software
PATH:=$(CURDIR)/conda/bin:$(PATH)
unexport PYTHONPATH
unexport PYTHONHOME

# install versions of conda for Mac or Linux
ifeq ($(UNAME), Darwin)
CONDASH:=Miniconda3-4.7.12-MacOSX-x86_64.sh
endif

ifeq ($(UNAME), Linux)
CONDASH:=Miniconda3-4.7.12-Linux-x86_64.sh
endif

CONDAURL:=https://repo.continuum.io/miniconda/$(CONDASH)

# install conda
conda:
	@echo ">>> Setting up conda..."
	@wget "$(CONDAURL)" && \
	bash "$(CONDASH)" -b -p conda && \
	rm -f "$(CONDASH)"

# install the conda and python packages required
install: conda
	conda install -y anaconda::pillow=8.0.0 python=3.7.4

# enter interactive bash session with the environment from the Makefile activated
bash:
	bash

# run unit test suite
test:
	./test_imagesort.py

# run all the test CLI commands
THREADS:=4
test-commands:
	set -eux
	mkdir -p thumbnail_output
	./imagesort.py print assets/ --threads $(THREADS) --ignore ignore-pixels-white.jpg
	./imagesort.py print assets/ --threads $(THREADS) --ignore ignore-pixels-white.jpg > data.csv
	./imagesort.py print assets/ --key red --threads $(THREADS) --ignore ignore-pixels-white.jpg > red.csv
	./imagesort.py thumbnails assets/ --output thumbnail_output/ --threads $(THREADS)
	./imagesort.py thumbnails assets/ --output thumbnail_output/ --threads $(THREADS) -x 200 -y 200 --bar 60
	./imagesort.py thumbnails assets/ --output thumbnail_output/ --key red --threads $(THREADS) -x 200 -y 200 --bar 60
	./imagesort.py thumbnails data.csv --output thumbnail_output/ -x 200 -y 200 --bar 60 --csv
	./imagesort.py collage assets/ --output collage.jpg --threads $(THREADS)
	./imagesort.py collage assets/ --output collage.jpg --threads $(THREADS) --key red
	./imagesort.py collage data.csv --output collage.jpg --csv -x 200 -y 200 --bar 60 --ncol 5
	./imagesort.py gif assets/ --output image.gif --threads $(THREADS) -x 200 -y 200 --bar 60
	./imagesort.py gif assets/ --output red.gif --threads $(THREADS) -x 200 -y 200 --bar 60 --key red
	./imagesort.py gif data.csv --output image.gif --csv -x 200 -y 200 --bar 60


VERSION=latest
DOCKERTAG:=stevekm/image-sort:$(VERSION)
docker-build:
	docker build -t "$(DOCKERTAG)" .
# docker push stevekm/image-sort:latest

docker-test:
	docker run --rm -ti "$(DOCKERTAG)" test_imagesort.py
