#!/bin/bash

printf "\n>>>> Execute unige_local_check_jobs.bash \n\n"

n_total=`ls | grep "job_" | grep -v log | wc -l`
n_running=`ps -ef | grep "/bin/bash ./job_" | grep -v 'grep' | wc -l`

echo ""
echo "Total number of jobs: ${n_total}"
echo "Number of running jobs: ${n_running}"
echo ""

ps -ef | grep "/bin/bash ./job_" | grep -v 'grep'

for dir in `ls /tmp | grep skim`
do 
    echo "${dir}"
    ls /tmp/${dir} | grep tmp 
    cat /tmp/${dir}/*/*prog* | tail -n1
done
date

echo ${n_running} > ../../../tmp
