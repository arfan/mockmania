#!/usr/bin/env bash
nohup python main.py &
sleep 3
python sample_use.py
echo lastLine
kill -9 $(sudo lsof -t -i:7000)

rm nohup.out