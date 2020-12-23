FROM python:3.8

WORKDIR /code

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /code

RUN export SECRET_KEY=test_SECRET_KEY && python manage.py collectstatic --noinput