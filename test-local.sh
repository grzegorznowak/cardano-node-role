#!/bin/bash

rm localenv -rf
sudo apt install -y unzip virtualenv build-essential python3-dev
sudo apt install python-pip || true
sudo apt install python3-pip || true


virtualenv localenv --python=python3
. localenv/bin/activate
python -m pip install --upgrade pip
pip install -r local-requirements.txt

ansible-lint
molecule test -s local-cardano-node-role