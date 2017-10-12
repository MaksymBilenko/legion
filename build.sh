#!/usr/bin/env bash

cd base-python-image
docker build -t drun/base-python-image:latest .
cd ..

cd drun-edge
docker build -t drun/edge .
cd ..

cd grafana
docker build -t drun/grafana .
cd ..

cd jenkins
docker build -t drun/jenkins-server:latest .
cd ..