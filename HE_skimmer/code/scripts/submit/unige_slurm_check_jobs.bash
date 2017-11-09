#!/bin/bash
### NEEDS WORK! ####
printf "\n>>>> Execute unige_slurm_check_jobs.bash \n\n"

user="`cat ../../../parameters.txt | grep submit_user | awk '{print $2}'`"
queue="`cat ../../../parameters.txt | grep submit_queue | awk '{print $2}'`"
skim_version="`cat ../../../parameters.txt | grep skim_version | awk '{print $2}'`"

n_total=`ls | grep job_${skim_version} | grep -v '\.e' | grep -v '\.o' | wc -l`
n_submitted=`squeue -u ${user} -p ${queue} | grep job_${skim_version} | grep -v '\.e' | grep -v '\.o' | grep -v ' C ' | grep -v ' E ' | wc -l`
n_running=`squeue -u ${user} -p ${queue} | grep job_${skim_version} | grep -v '\.e' | grep -v '\.o' | grep ' R ' | wc -l`


echo ""
echo "Total number of jobs: ${n_total}"
echo "Number of submitted jobs: ${n_submitted}"
echo "Number of running jobs: ${n_running}"
echo ""

qstat -u ${user} | head -n5
qstat -u ${user} | grep ${queue} | grep job_${skim_version} | grep R | head -n20 | grep -v Req
echo "-------------------- -------- -------- ---------------- ------ ----- --- ------ ----- - -----"
qstat -u ${user} | grep ${queue} | grep job_${skim_version} | grep -v R | grep -v C | head -n20 | grep -v Req

echo ${n_submitted} > ../../../tmp

