FROM python:3.10

RUN mkdir -p /app/line-provider/src
WORKDIR /app/line-provider/src

COPY  . /app/line-provider

RUN : \
    && pip install --no-cache-dir -r /app/line-provider/requirements.txt \
    && :