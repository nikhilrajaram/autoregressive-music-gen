#!/bin/bash

../venv/bin/python python-parse.py $1
ts-node tonejs-parse.ts -- $1