FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1

RUN apk update && apk add --no-cache \
    curl \
    git \
 && pip install --upgrade pip poetry

RUN mkdir -p /app
COPY . /app
WORKDIR /app
RUN poetry install --no-root --only main

EXPOSE $PORT
CMD ["poetry", "run", "python", "app/main.py"]

