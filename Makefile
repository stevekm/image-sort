SHELL:=/bin/bash
UNAME:=$(shell uname)

# ~~~~~ Setup Conda ~~~~~ #
# this sets the system PATH to ensure we are using in included 'conda' installation for all software
PATH:=$(CURDIR)/conda/bin:$(PATH)
unexport PYTHONPATH
unexport PYTHONHOME

# install versions of conda for Mac or Linux
ifeq ($(UNAME), Darwin)
CONDASH:=Miniconda2-4.5.4-MacOSX-x86_64.sh
endif

ifeq ($(UNAME), Linux)
CONDASH:=Miniconda2-4.5.4-Linux-x86_64.sh
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
conda-install: conda
	conda install -y -c anaconda \
	python=2.7 \
	pil=1.1.7

CMD:=
cmd:
	$(CMD)

images.rgb.hsv.csv:
	./sort-images.py assets -o images.rgb.hsv.csv

sort: images.rgb.hsv.csv

filmstrip.jpg: images.rgb.hsv.csv
	./list2filmstrip.py -i images.rgb.hsv.csv -o filmstrip.jpg -x 200 -y 200

collage.jpg: images.rgb.hsv.csv
	./list2collage.py -i images.rgb.hsv.csv

test: filmstrip.jpg collage.jpg

run: sort filmstrip.jpg collage.jpg

clean:
	rm -f images.rgb.hsv.csv
	rm -f filmstrip.jpg collage.jpg
