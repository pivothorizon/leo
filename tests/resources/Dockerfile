FROM ubuntu:18.04

ENV APP_DIR /app
ENV PACKAGE_NAME testleo

WORKDIR ${APP_DIR}

RUN apt-get update --fix-missing
RUN apt-get install -q -y openjdk-8-jre-headless ca-certificates-java && \
    apt-get install -q -y python3-gevent python3-pip && \
    apt-get install -q -y gnupg
RUN apt-get -o Dpkg::Options::="--force-confmiss" install --reinstall netbase


COPY requirements.txt ${APP_DIR}/
COPY models ${APP_DIR}/models

RUN cp /usr/bin/python3 /usr/bin/python

# Install python requirements from PyPi
RUN pip3 install -r requirements.txt

ADD ${PACKAGE_NAME} ${APP_DIR}/${PACKAGE_NAME}

EXPOSE 5000
# Use Gunicorn as a standalone wsgi container in production mode.
# Add "--workers" or "-w" for spinning up number of workers you would like. Recommended formula for calculating number of workers: 2 * cpu + 1.
# Example for 4 cpu machine: 2 * 4 + 1 = 9. You can set it by adding options before the last argument of the ENTRYPOINT.

# Gunicorn is based on the pre-fork worker model. Default worker class is "sync" which handles requests synchronously.
# You can change default worker class by setting "-k" option
# Example: Using eventlet for async request handling. "-k", "eventlet"

# There are a lot more configuration parameters which you can modify.
# For more details on how to configure Gunicorn please refer to official documenttion here: http://docs.gunicorn.org/en/stable/settings.html
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:5000", "--log-level", "debug", "-c" ,\
            "testleo/config.py", "-k", "eventlet", "--timeout", "120", "--workers", "9", "testleo:application"]

