#!/bin/bash

python_exe=python
if ! command -v $python_exe &> /dev/null
then
    python_exe=python3
fi
$python_exe -m venv .venv
. .venv/bin/activate
export LDFLAGS="-I/usr/local/opt/openssl/include -L/usr/local/opt/openssl/lib"
pip install --upgrade pip
pip install -r requirements.txt
cd src/
pip install -e .
