SHELL:=/bin/bash
UNAME:=$(shell uname)
export NXF_VER:=19.01.0

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
# NOTE: **MUST** install ncurses from conda-forge for RabbitMQ to work!!
conda-install: conda nextflow
	conda install -y -c anaconda \
	python=2.7 \
	pil=1.1.7 \

CMD:=
cmd:
	$(CMD)


IMGDIR:=assets
OUTPUTLIST:=images.rgb.hsv.csv
$(OUTPUTLIST):
	./sort-images.py "$(IMGDIR)" -o "$(OUTPUTLIST)"

sort: $(OUTPUTLIST)

filmstrip.jpg: $(OUTPUTLIST)
	./list2filmstrip.py -i $(OUTPUTLIST) -o filmstrip.jpg -x 200 -y 200

collage.jpg: $(OUTPUTLIST)
	./list2collage.py -i $(OUTPUTLIST)

test: filmstrip.jpg collage.jpg

# run: sort filmstrip.jpg collage.jpg

EP:=
run:
	./nextflow run main.nf $(EP)





clean:
	rm -f $(OUTPUTLIST)
	rm -f filmstrip.jpg collage.jpg
	rm -f .nextflow.log*


docker-build:
	docker build -t stevekm/image-sort .

docker-test:
	docker run --rm -ti stevekm/image-sort bash
