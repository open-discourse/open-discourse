#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate
export LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib"
pip install -r requirements.txt
cd src/
pip install -e .
