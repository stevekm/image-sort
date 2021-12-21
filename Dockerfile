# replicate continuumio/miniconda:4.7.12 because building from that base image keeps giving error for:
# E: Repository 'http://security.debian.org/debian-security buster/updates InRelease' changed its 'Suite' value from 'stable' to 'oldstable'
FROM debian:stretch

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

ENV PATH /usr/conda/bin:$PATH

RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 ca-certificates curl git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-4.7.12-Linux-x86_64.sh -O ~/miniconda.sh && \
/bin/bash ~/miniconda.sh -b -p /usr/conda && \
rm ~/miniconda.sh && \
/usr/conda/bin/conda clean -tipsy && \
ln -s /usr/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
echo ". /usr/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
echo "conda activate base" >> ~/.bashrc

ENV TINI_VERSION v0.16.1
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini

ENTRYPOINT [ "/usr/bin/tini", "--" ]
CMD [ "/bin/bash" ]

# install extra libraries into base env
RUN apt-get update && apt-get install -y imagemagick
RUN conda install -y anaconda::pillow=8.0.0 python=3.7.4

# add this repo contents
RUN mkdir -p /image-sort
ADD img.py /image-sort/img.py
ADD test_img.py /image-sort/test_img.py
ADD fixtures /image-sort/fixtures
ADD assets /image-sort/assets
ENV PATH="/image-sort:${PATH}"
WORKDIR /image-sort
