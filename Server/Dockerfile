FROM ubuntu:latest

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends aria2 unzip wget curl python3 python3-pip build-essential
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash
RUN apt install -y nodejs
COPY . . 

RUN npm i -g localtunnel
RUN pip3 install -r requirements.txt
RUN apt-cache policy aria2

CMD aria2c --enable-rpc --console-log-level=error --seed-time=0.01 --max-connection-per-server=16 --bt-stop-timeout=480 & python3 api.py & lt --port 5000 --subdomain pellmirror
