#!/bin/bash

data_location="/data/PMO_cluster/2A"

for pid in `ps -ef | grep rsync | grep "${data_location}" | grep -v grep | awk '{print $2}'`
do
    echo "Kill ${pid}"
    kill -9 ${pid}
done
