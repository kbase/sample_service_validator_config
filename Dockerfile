FROM alpine:3.14
MAINTAINER KBase Developer

# update and add system dependencies
RUN apk upgrade --update-cache --available && \
    apk add --update --no-cache bash g++ git libffi-dev linux-headers \
    make openssl-dev python3 python3-dev py3-setuptools py3-pip py3-pandas py3-yaml py3-jsonschema

COPY ./ /kb/module

WORKDIR /kb/module

#RUN pip install -r requirements.txt

ENTRYPOINT ["bash", "/kb/module/scripts/run_tests.sh"]