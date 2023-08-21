FROM python:3.10

RUN mkdir -p /app/bet-maker/src
WORKDIR /app/bet-maker/src

COPY  . /app/bet-maker

RUN : \
    && pip install --no-cache-dir -r /app/bet-maker/requirements.txt \
    && :