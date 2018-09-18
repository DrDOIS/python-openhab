FROM ubuntu:latest

RUN apt update && apt -y upgrade \
  && apt install -y git python3.6 python3-pip 

RUN git clone https://github.com/DrDOIS/python-openhab.git \
  && cd python-openhab \
  && pip3 install requests python-dateutil paho-mqtt


ENTRYPOINT python3 /python-openhab/test.py

# BUILD: docker build . -t openhabrules
# RUN:   docker run -d --name openhab_rules openhabrules
