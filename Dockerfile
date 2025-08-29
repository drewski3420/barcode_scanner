FROM python:3.10-slim
#FROM python:3.10-slim-bullseye

WORKDIR /app

#Install dependencies
COPY requirements.txt .

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt update && \
    apt install -y wget curl nano ffmpeg \
    build-essential \
    pkg-config \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install -r requirements.txt

COPY index.py .

##Create user and crontab
#RUN groupadd --gid 1001 appgroup && \
#    adduser --uid 1000 --gid 1001 --no-create-home --disabled-password --gecos "" appuser

#COPY cron.file /tmp/mycron
#RUN crontab -u $APP_USER /tmp/mycron
#RUN chmod 600 /var/spool/cron/crontabs/$APP_USER

#Run it
ENTRYPOINT ["python3", "/app/flask"]
