#!/usr/bin/env bash
nohup python main.py &
sleep 3
python sample_use.py
echo lastLine

kill -9 $(lsof -t -i:7000 -sTCP:LISTEN)

rm nohup.out