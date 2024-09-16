FROM python:3.12

RUN apt update -y && apt upgrade -y
RUN pip install --upgrade pip
COPY requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt
RUN mkdir "/app"
COPY ./kolyan.py /app/
COPY ./bot_config.conf /app/
COPY ./entrypoint.sh /
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
