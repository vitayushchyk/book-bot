FROM python:3.12-slim AS base

ARG APP_ENV
ENV APP_ENV=${APP_ENV:-development} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unzip \
    && apt-get clean

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock ./README.md /app/
RUN poetry install --no-root --only main

COPY . ./

CMD ["poetry", "run", "python", "main.py"]
