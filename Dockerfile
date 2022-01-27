FROM alpine:3.15
LABEL org.opencontainers.image.authors="KBase Developer"

# update and add system dependencies
RUN apk upgrade --update-cache --available && \
    apk add --update --no-cache bash g++ git libffi-dev linux-headers \
    make openssl-dev python3 python3-dev py3-setuptools py3-pip py3-pandas \
    py3-yaml py3-jsonschema py3-gitpython

WORKDIR /kb/tmp

COPY requirements-docker.txt .

RUN pip install -r requirements-docker.txt

WORKDIR /kb/module

ENTRYPOINT ["bash"]

CMD []