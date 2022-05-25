#!/bin/bash

python3 -m venv .venv
. .venv/bin/activate
export LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib"
pip install --upgrade pip
pip install -r requirements.txt
cd src/
pip install -e .
