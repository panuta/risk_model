FROM python:3.6-alpine3.6
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache \
        bash \
        build-base \
        libffi-dev \
        openssl-dev \
        libxml2-dev \
        libxslt-dev

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements
RUN pip install -r /requirements/develop.txt

COPY ./compose/server/start.sh /start.sh
RUN sed -i 's/\r//' /start.sh
RUN chmod +x /start.sh

WORKDIR /app

ENTRYPOINT ["/start.sh"]
