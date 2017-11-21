#!/bin/bash

virtualenv venv
. ./venv/bin/activate
pip install -r requirements.txt

exec $(which bash) 
