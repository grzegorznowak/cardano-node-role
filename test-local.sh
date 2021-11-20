#!/bin/bash

sudo apt install -y curl unzip virtualenv build-essential python3-dev
sudo apt install python-pip || true
sudo apt install python3-pip || true


test -d localenv || virtualenv localenv --python=python3
. localenv/bin/activate
python -m pip install --upgrade pip
pip install -r local-requirements.txt

python -m pytest tests

ansible-lint
molecule test -s local-test-cardano-node-role