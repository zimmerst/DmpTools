#!/bin/bash
# extreme dirty monitor to check crawler progress
wd=$(pwd)
td=${1} # crawler output directory

check(){
    ndone=$(grep -o "lfn" ${task}.json | wc -w)
    ntotal=$(wc -l ${task}.txt | awk '{print $1}')
    echo "${task}: ${ndone}/${ntotal}"
}

cd ${td}
for f in $(ls | grep "json" | awk -F ".json" '{print $1}');
do
    export task=${f}
    check
done