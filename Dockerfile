FROM debian:stretch

RUN apt-get update

RUN apt-get install -y python3 python3-pip
RUN apt-get install -y git sassc

RUN ln -s python3 /usr/bin/python && ln -s pip3 /usr/bin/pip
WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

ENV PYTHONPATH /app
ADD kw /app/kw
ADD vagla /app/vagla
ENV DJANGO_SETTINGS_MODULE vagla.settings

ENTRYPOINT ["gunicorn", "vagla.wsgi", "-k", "gevent", "-b", "0.0.0.0:80"]
