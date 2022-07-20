FROM python:3.9-slim

COPY . /usr/src/app
WORKDIR /usr/src/app

RUN apt update && \
    pip install --upgrade pip && \
    apt-get install -y git libgdal-dev g++ gettext --no-install-recommends && \
    apt-get clean -y

RUN pip install -r requirements.txt

WORKDIR /usr/src/app

CMD ["./startup.sh"]
