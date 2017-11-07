FROM library/ubuntu:16.04

ADD requirements.txt /root/requirements.txt

# Theano requires C++ compiler to produce effective code
RUN apt-get update && apt-get install -y --no-install-recommends python3 \
    g++ apt-utils python3-dev python3-pip python3-setuptools file wget git \
    libtiff5-dev libjpeg8-dev zlib1g-dev \
    tcl8.6-dev tk8.6-dev python-tk python3-tk \
    libfreetype6-dev liblcms2-dev libwebp-dev libharfbuzz-dev libfribidi-dev \
    curl \
    echo "deb [arch=amd64] http://storage.googleapis.com/tensorflow-serving-apt stable tensorflow-model-server tensorflow-model-server-universal" | tee /etc/apt/sources.list.d/tensorflow-serving.list && \
    curl https://storage.googleapis.com/tensorflow-serving-apt/tensorflow-serving.release.pub.gpg | apt-key add - && \
    apt-get update && apt-get install -y tensorflow-model-server && \
    rm -rf /var/lib/apt/lists/*


RUN pip3 install --upgrade pip \
    && pip3 install -r /root/requirements.txt

WORKDIR /app
