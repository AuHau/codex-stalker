FROM python:3.12-slim-bookworm
LABEL authors="adam@uhlir.dev"

WORKDIR /usr/src/app

ENV CODEX_API_URL="http://host.docker.internal:8080"

VOLUME /usr/src/data
ENV DB="/usr/src/data/database.db"
RUN mkdir -p /usr/src/data/ && apt update && apt install -y git

COPY . .

RUN pip install -r requirements.txt
RUN ./manage.py migrate --noinput

ENTRYPOINT python main.py
