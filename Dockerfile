FROM continuumio/miniconda:4.4.10

MAINTAINER Stephen M. Kelly

RUN apt-get update && apt-get install -y imagemagick make default-jre
RUN conda install -y -c anaconda pil=1.1.7
RUN git clone https://github.com/stevekm/image-sort.git && \
cd /image-sort && \
make nextflow
ENV PATH="/image-sort:/image-sort/bin:${PATH}"
WORKDIR /image-sort
