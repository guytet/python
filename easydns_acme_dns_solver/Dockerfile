FROM python:3.12-rc-slim

ARG DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install --no-install-recommends -qqy \
        procps \
        curl \
    && apt-get upgrade -qqy \
    && rm -rf /var/lib/apt/lists

WORKDIR /app

COPY ./requirements.txt /app/
COPY ./easydns_acme_solver.py /app/

RUN pip install -r requirements.txt

ENTRYPOINT ["gunicorn", "--certfile=/etc/tls/tls.crt", "--keyfile=/etc/tls/tls.key", "-b", "0.0.0.0:8443", "easydns_acme_solver:app"]

