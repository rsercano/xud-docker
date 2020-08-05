FROM python:3.8.2-alpine3.11
RUN apk --no-cache add docker-cli docker-compose
RUN pip install toml docker demjson
ADD . /usr/local/src/utils
WORKDIR /usr/local/src/utils
RUN python setup.py install
WORKDIR /root
