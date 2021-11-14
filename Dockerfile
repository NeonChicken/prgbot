FROM python:3.9.8-slim-bullseye
RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean
COPY requirements.txt /
RUN pip3 install -r requirements.txt
COPY . /
ENTRYPOINT [ "python3", "-u", "prgbot.py" ]
