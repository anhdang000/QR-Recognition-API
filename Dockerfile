FROM ubuntu:18.04

ADD . /workspace
WORKDIR /workspace

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install openjdk-8-jre -y

RUN pip install -r requirements.txt
RUN pip install gunicorn
RUN chmod +x boot.sh

ENV FLASK_APP server.py
EXPOSE 80
ENTRYPOINT ["./boot.sh"]
