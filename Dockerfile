FROM python:3.7-slim-buster
LABEL org.opencontainers.image.authors="KBase Developer"

# update and add system dependencies
RUN apt-get -y update && \
    pip install --upgrade pip

WORKDIR /kb/tmp

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /kb/module

ENTRYPOINT ["bash"]

CMD []