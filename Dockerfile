FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1

RUN apk update && apk add --no-cache \
    libpq \
    gcc \
    libressl-dev \
    libffi-dev \
    build-base \
    curl

RUN pip install --upgrade pip poetry

RUN mkdir -p /app
COPY . /app
WORKDIR /app
RUN poetry install --no-root --no-dev

EXPOSE $PORT
CMD ["poetry", "run", "python", "app/proxy.py"]

