FROM python:3.8-slim

RUN \
    pip install --upgrade pip \
 && pip install gunicorn

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 80/tcp
CMD ["gunicorn", "--log-level=debug", "--bind=0.0.0.0:80", "--log-file=-", "wsgi:app"]
