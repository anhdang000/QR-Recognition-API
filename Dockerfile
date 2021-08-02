FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"
RUN apt-get update

RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*

RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh 
RUN conda --version

ADD . /workspace
WORKDIR /workspace

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install openjdk-8-jre -y

# Create conda environment
RUN conda env create -f environment.yaml

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "qr-code", "/bin/bash", "-c"]

RUN wget https://martin-krasser.de/sisr/weights-wdsr-b-32-x4.tar.gz
RUN tar xvfz weights-wdsr-b-32-x4.tar.gz

RUN python -c "from model.edsr import edsr"

ENTRYPOINT ["conda", "run", "-n", "qr-code", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80", "--reload"]

