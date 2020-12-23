FROM python:3.8.5

WORKDIR /code
COPY requirements.txt .
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . /code
RUN export SECRET_KEY=test_SECRET_KEY && python manage.py collectstatic --noinput