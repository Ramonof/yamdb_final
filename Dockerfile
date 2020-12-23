FROM python:3.8

WORKDIR /code

COPY requirements.txt .
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /code

RUN export SECRET_KEY=test_SECRET_KEY && python manage.py collectstatic --noinput
