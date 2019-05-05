FROM ubuntu:16.04

MAINTAINER Stephen M. Kelly

RUN apt-get update && \
apt-get install -y wget \
bzip2 \
git

RUN wget https://repo.continuum.io/miniconda/Miniconda2-4.5.12-Linux-x86_64.sh && \
bash Miniconda2-4.5.12-Linux-x86_64.sh -b -p /conda && \
rm -f Miniconda2-4.5.12-Linux-x86_64.sh
ENV PATH="/conda/bin:${PATH}"
RUN conda install -y -c anaconda \
python=2.7 \
pil=1.1.7
RUN git clone https://github.com/stevekm/image-sort.git
