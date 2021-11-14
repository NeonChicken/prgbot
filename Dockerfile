FROM python:3.9.8-bullseye
COPY . /
RUN pip3 install -r requirements.txt
ENTRYPOINT [ "python3", "prgbot.py" ]
