FROM python:3.12-slim AS base

ENV APP_ENV=development \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.7.1


RUN apt-get update && apt-get install -y curl gnupg unzip && apt-get clean
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"


WORKDIR /app


COPY ./pyproject.toml ./poetry.lock /app/
RUN poetry install --no-root --only main


COPY . .


CMD ["poetry", "run", "python", "main.py"]
