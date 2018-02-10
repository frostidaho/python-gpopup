FROM debian:stretch-slim
ENV LANG C.UTF-8
WORKDIR /app
RUN apt-get update && apt-get install --no-install-recommends -y \
    gir1.2-gtk-3.0 \
    python3-gi \
    python3-setuptools \
    python3-wheel \
    python3-pip \
    python3-pytest-cov

RUN apt-get install --no-install-recommends -y \
    python-gi \
    python-gi-cairo \
    python-setuptools \
    python-wheel \
    python-pip \
    python-pytest-cov

RUN apt-get install --no-install-recommends -y \
    xauth \
    xvfb

# jq is required for one of the example scripts
RUN apt-get install --no-install-recommends -y \
    jq
