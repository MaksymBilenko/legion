#Airflow Image
FROM ubuntu:16.04

ENV AIRFLOW_HOME /home/airflow

RUN apt-get update && apt-get install -y \
 wget \
 default-jdk \
 python3.5 \
 python3.5-dev \
 vim \
 cron \
 libkrb5-dev \
 libsasl2-dev \
 libssl-dev \
 libffi-dev \
 build-essential \
 libblas-dev \
 liblapack-dev \
 python3-pip \
 apt-utils \
 curl \
 netcat \
 iputils-ping \
 openssh-client \
 python-requests \
 libpq-dev \
 libmysqlclient-dev \
 sshpass \
 sudo \
 redis-tools

RUN service cron stop \
 && useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow

RUN pip3 install --upgrade pip \
 && pip3 install Cython \
 && pip3 install cryptography \
 && pip3 install apache-airflow[postgres,jdbc,password,mysql,celery,redis,s3]==1.9.0 \
 && pip3 install pyOpenSSL \
 && pip3 install ndg-httpsclient \
 && pip3 install pyasn1 \
 && pip3 install psycopg2-binary \
 && pip3 install redis \
 && pip3 install hiredis \
 && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base

COPY entrypoint.sh /home/airflow/init.sh

COPY requirements.txt /home/airflow/requirements.txt
RUN pip install -r /home/airflow/requirements.txt

RUN chown -R airflow: ${AIRFLOW_HOME} && chmod -R 775 ${AIRFLOW_HOME}

RUN chmod a+x /home/airflow/init.sh

EXPOSE 8080

USER airflow
WORKDIR ${AIRFLOW_HOME}

ENTRYPOINT ["sh", "/home/airflow/init.sh"]