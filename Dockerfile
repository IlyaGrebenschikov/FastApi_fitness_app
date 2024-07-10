FROM python:3.10.12-buster
EXPOSE 8080

WORKDIR /usr/app/backend
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apt update
RUN pip install --upgrade pip
RUN pip install poetry
COPY . .
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-interaction --no-ansi