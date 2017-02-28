#!/usr/bin/env bash
# should be dispatched in daemon mode:
# setsid crawlerAgent > crawlerAgent.log 2>&1 < /dev/null &
#
# MODIFY ME
CRAWLER_ROOT="/path/to/DmpTools/crawler"
root_dir="/dampe/data3/mc/.../"
crawler_output="/path/to/where/crawler/writes/json"

# DO NOT MODIFY THIS!
export CRAWLER="${CRAWLER_ROOT}/crawler.py"
cycles=0

mkdir -p ${crawler_output}/old_runs

while true;
do
    pids=""
    echo "$(date): starting cycle ${cycles}"
    cd ${root_dir}
    for task in $(ls .);
    do
        echo "crawling ${task} ..."
        tfile=${crawler_output}/${task}.txt
        if [ -f ${tfile} ];
        then
            cp ${tfile} ${crawler_output}/old_runs/${task}.txt
        fi
        find $(readlink -f ${task}) -type f >> ${tfile}

        if [ -f ${crawler_output}/old_runs/${task}.txt ];
        then
            file_a=${crawler_output}/old_runs/${task}.txt
            file_b=${tfile}
            comm <(sort ${file_a}) <(sort ${file_b}) -3 > ${tfile}
        fi
        nf=$(wc -l ${tfile} | awk '{print $1}')
        if [ "$nf" -gt 0 ];
        then
            cd ${crawler_output}
            bash ${CRAWLER_ROOT}/crawl_filelist.sh ${tfile} &
            pids+="$! "
        else
            echo "nothing to do"
        fi
    done
    echo "$(date): waiting for subprocesses to be finished"
    for pid in $pids;
    do
        wait ${pid}
        if [ $? -eq 0 ]; then
            echo "SUCCESS - child process $pid exited with a status of $?"
        else
            echo "FAILED - child process $pid exited with a status of $?"
        fi
    done
done