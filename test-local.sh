#!/bin/bash

rm testingenv -rf
sudo apt install -y unzip virtualenv build-essential python3-dev
sudo apt install python-pip || true
sudo apt install python3-pip || true


virtualenv testingenv --python=python3
. testingenv/bin/activate
pip install -r tests-requirements.txt

molecule test -s local-cardano-node-role