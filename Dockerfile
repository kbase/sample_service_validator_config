FROM alpine:3.14
LABEL org.opencontainers.image.authors="KBase Developer"

COPY ./ /kb/module

WORKDIR /kb/module

# update and add system dependencies
RUN apk upgrade --update-cache --available && \
    apk add --update --no-cache bash g++ git libffi-dev linux-headers \
    make openssl-dev python3 python3-dev py3-setuptools py3-pip py3-pandas \
    py3-yaml py3-jsonschema py3-gitpython && \
    pip install -r requirements-docker.txt

ENTRYPOINT ["bash"]

CMD ["/kb/module/scripts/run_tests.sh"]