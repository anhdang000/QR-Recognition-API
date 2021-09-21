FROM conda/miniconda3

ADD . /workspace
WORKDIR /workspace

RUN apt-get update
RUN apt install build-essential -y
RUN apt-get install manpages-dev -y
RUN apt-get install zbar-tools -y
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install openjdk-8-jre -y
RUN apt-get install libzbar0 -y

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN chmod +x boot.sh

ENV FLASK_APP server.py
EXPOSE 80
ENTRYPOINT ["./boot.sh"]
