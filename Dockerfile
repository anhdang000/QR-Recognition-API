FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04

RUN apt-get update && apt-get install -y --no-install-recommends \
         build-essential \
         cmake \
         git \
         curl \
         vim \
         ca-certificates \
         libboost-all-dev \
         python-qt4 \
         libjpeg-dev \
         libpng-dev &&\
     rm -rf /var/lib/apt/lists/*

# For opencv requirements
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install openjdk-8-jre

RUN curl -o ~/miniconda.sh -O  https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh  && \
     chmod +x ~/miniconda.sh && \
     ~/miniconda.sh -b -p /opt/conda && \
     rm ~/miniconda.sh

ENV PATH /opt/conda/bin:$PATH
# ENV CUDA_VISIBLE_DEVICES=1

RUN conda config --set always_yes yes --set changeps1 no && conda update -q conda 
RUN conda install -c anaconda pip

# Install face-alignment package
WORKDIR /workspace
RUN chmod -R a+w /workspace
ADD . /workspace/
RUN pip install -r requirements.txt

EXPOSE 80
ENTRYPOINT ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
