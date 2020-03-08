#!/usr/bin/env bash
nohup python main.py &
sleep 3
python sample_use.py
kill -9 $(lsof -t -i:7000 -sTCP:LISTEN)
rm -f nohup.out
echo mocks > mocks_folder
echo lastLine
