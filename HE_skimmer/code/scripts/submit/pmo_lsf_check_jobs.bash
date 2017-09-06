#!/bin/bash

printf "\n>>>> Execute pmo_lsf_check_jobs.bash \n\n"

user="`cat ../../../parameters.txt | grep submit_user | awk '{print $2}'`"
queue="`cat ../../../parameters.txt | grep submit_queue | awk '{print $2}'`"

rm -f tmp.jobs
for job in `bjobs | grep ${user} | awk '{print $1}'`
do 
    bjobs -l ${job} >> tmp.jobs
done

n_total=`ls | grep "job_" | wc -l`
n_submitted=`cat tmp.jobs | grep ${user} | wc -l`
n_running=`cat tmp.jobs | grep ${user} | grep Status | grep RUN | wc -l`

echo ""
echo "Total number of jobs: ${n_total}"
echo "Number of submitted jobs: ${n_submitted}"
echo "Number of running jobs: ${n_running}"
echo ""

bjobs

rm -f tmp.jobs

echo ${n_submitted} > ../../../tmp
