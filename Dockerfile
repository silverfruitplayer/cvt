FROM debian:latest

RUN apt update && apt upgrade -y
RUN apt install git curl python3-pip ffmpeg -y
RUN cd /
RUN git clone https://github.com/silverfruitplayer/cvt
RUN cd cvt
WORKDIR /cvt
RUN pip3 install -r requirements.txt
CMD python3 cvt.py
