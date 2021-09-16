#!/bin/bash

export PATH=$PATH:{{ ghc_bin_path }}
export LD_LIBRARY_PATH="/usr/local/lib:$LD_LIBRARY_PATH"
export PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH"

cd {{ cardano_src_path }}/cardano-node
git fetch --all --recurse-submodules --tags
git checkout tags/{{ cardano_node_version }}

cabal configure --with-compiler=ghc-{{ ghc_version }}

echo "package cardano-crypto-praos" >>  cabal.project.local
echo "  flags: -external-libsodium-vrf" >>  cabal.project.local

cabal build all

export PATH="{{ cardano_bin_path }}/:$PATH"
