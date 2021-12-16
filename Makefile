SHELL:=/bin/bash
UNAME:=$(shell uname)
export NXF_VER:=19.01.0

# requires Java installation
nextflow:
	curl -fsSL get.nextflow.io | bash

# ~~~~~ Setup Conda ~~~~~ #
# this sets the system PATH to ensure we are using in included 'conda' installation for all software
PATH:=$(CURDIR)/conda/bin:$(PATH)
unexport PYTHONPATH
unexport PYTHONHOME

# install versions of conda for Mac or Linux
ifeq ($(UNAME), Darwin)
CONDASH:=Miniconda2-4.4.10-MacOSX-x86_64.sh
endif

ifeq ($(UNAME), Linux)
CONDASH:=Miniconda2-4.4.10-Linux-x86_64.sh
endif

CONDAURL:=https://repo.continuum.io/miniconda/$(CONDASH)

# install conda
conda:
	@echo ">>> Setting up conda..."
	@wget "$(CONDAURL)" && \
	bash "$(CONDASH)" -b -p conda && \
	rm -f "$(CONDASH)"

# install the conda and python packages required
# NOTE: also need to install imagemagick but it appears to be broken with these versions of other conda packages
conda-install: conda nextflow
	conda install -y -c anaconda pil=1.1.7 && \
	printf ">>> Make sure that imagemagick is installed;\n[Ubuntu]: apt-get install -y imagemagick\n[Mac]: brew install imagemagick\n" || \
	echo ">>> Error encountered while trying to install conda packages"

CMD:=
cmd:
	$(CMD)

# enter interactive bash session with the environment from the Makefile activated
bash:
	bash

# IMGDIR:=assets
# OUTPUTLIST:=images.rgb.hsv.csv
# $(OUTPUTLIST):
# 	./sort-images.py "$(IMGDIR)" -o "$(OUTPUTLIST)"
#
# sort: $(OUTPUTLIST)
# filmstrip.jpg: $(OUTPUTLIST)
# 	./list2filmstrip.py -i $(OUTPUTLIST) -o filmstrip.jpg -x 200 -y 200

OUTPUTDIR=output
# make run EP='--imgdir example_images --ignorePixels ignore-pixels-woodgrain.jpg'
EP:=
run:
	./nextflow run main.nf $(EP)

collage: $(OUTPUTDIR)/imgs.rgb.hsv.csv
	./bin/csv2collage.py -i $(OUTPUTDIR)/imgs.rgb.hsv.csv -o $(OUTPUTDIR)/collage.jpg

thumbnails: $(OUTPUTDIR)/imgs.rgb.hsv.csv $(OUTPUTDIR)/thumbnails
	./bin/csv2thumbnails.py -i $(OUTPUTDIR)/imgs.rgb.hsv.csv -o $(OUTPUTDIR)/thumbnails

# requires imagemagick; sudo apt-get install imagemagick
NUM_JPG:=$(shell find $(OUTPUTDIR)/thumbnails/ -name "*.jpg" | wc -l | tr -d ' ')
gif:
	convert -resize 90% -delay 10 -loop 0 $(OUTPUTDIR)/thumbnails/{1..$(NUM_JPG)}.jpg $(OUTPUTDIR)/sequence.gif


clean:
	rm -f filmstrip.jpg collage.jpg
	rm -f .nextflow.log*
	rm -f nextflow.html*
	rm -f timeline.html*
# rm -f $(OUTPUTLIST)

docker-build:
	docker build -t stevekm/image-sort .

docker-test:
	mkdir -p docker-output/thumbnails
	docker run --rm -ti -v "$${PWD}/docker-output:/output" stevekm/image-sort bash -c 'cd /image-sort && nextflow run main.nf --outputDir /output && make thumbnails OUTPUTDIR=/output && make gif OUTPUTDIR=/output && mv *.html /output/'
