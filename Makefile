SHELL:=/bin/bash
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


# requires imagemagick; sudo apt-get install imagemagick
# NUM_JPG:=$(shell find $(OUTPUTDIR)/thumbnails/ -name "*.jpg" | wc -l | tr -d ' ')
# gif:
# 	convert -resize 90% -delay 10 -loop 0 $(OUTPUTDIR)/thumbnails/{1..$(NUM_JPG)}.jpg $(OUTPUTDIR)/sequence.gif


VERSION=latest
DOCKERTAG:=stevekm/image-sort:$(VERSION)
docker-build:
	docker build -t "$(DOCKERTAG)" .
# docker push stevekm/image-sort:latest

docker-test:
	docker run --rm -ti "$(DOCKERTAG)" test_imagesort.py
