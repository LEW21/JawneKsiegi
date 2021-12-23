FROM python:3.10.1-alpine3.15

RUN ln -s python3 /usr/bin/python && ln -s pip3 /usr/bin/pip
WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

ENV PYTHONPATH /app
ADD kw /app/kw
ADD jawneksiegi /app/jawneksiegi
ENV DJANGO_SETTINGS_MODULE jawneksiegi.settings

ENTRYPOINT ["gunicorn", "jawneksiegi.wsgi", "-k", "gevent", "-b", "0.0.0.0:80"]
EXPOSE 80
