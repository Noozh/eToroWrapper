#!/bin/bash
netstat -tulpn | grep 5000
if [ $? -ne 0 ]
then
    id=$(docker ps | awk -F '        ' '{print $1}'| tail -1)
    docker stop $id
    docker run -d -p 5000:5000 core
    exit
fi

ps aux | grep "chromedriver --port" | grep -v grep
if [ $? -ne 0 ]
then
    id=$(docker ps | awk -F '        ' '{print $1}'| tail -1)
    docker stop $id
    docker run -d -p 5000:5000 core
fi
