FROM python:3.7-alpine3.15
LABEL org.opencontainers.image.authors="KBase Developer"

# update and add system dependencies
RUN apk upgrade --update-cache --available && \
    apk add --update --no-cache bash git && \
    pip install --upgrade pip

WORKDIR /kb/tmp

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /kb/module

ENTRYPOINT ["bash"]

CMD []