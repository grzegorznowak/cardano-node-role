#!/bin/bash

cd {{ cardano_src_path }}/libsodium
git checkout 66f017f1
./autogen.sh
./configure
make
sudo make install