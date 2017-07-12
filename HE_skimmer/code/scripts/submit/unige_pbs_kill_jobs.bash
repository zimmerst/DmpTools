#!/bin/bash

printf "\n>>>> Execute unige_pbs_kill_jobs.bash \n\n"

user="`cat ../../../parameters.txt | grep submit_user | awk '{print $2}'`"
queue="`cat ../../../parameters.txt | grep submit_queue | awk '{print $2}'`"
skim_version="`cat ../../../parameters.txt | grep skim_version | awk '{print $2}'`"

for job in $(qstat -u ${user} | grep ${queue} | grep job_${skim_version} | grep -v " C " | awk '{print $1}' | sed -e 's/\..*//')
do 
    echo "Kill job ${job}"
    qdel ${job}
done

ps -ef | grep "/bin/bash ./run.bash run ${skim_version}" | grep -v 'grep' | grep  -v kill
njobs=`ps -ef | grep "/bin/bash ./run.bash run ${skim_version}" | grep -v 'grep' | grep -v kill | wc -l`
if [ ${njobs} -ne 0 ]
then
    for pid in `ps -ef | grep "/bin/bash ./run.bash run ${skim_version}" | grep -v 'grep' | grep -v kill | awk '{print $2}'`
    do
	echo "Kill job ${pid}"
	kill -9 ${pid}
    done
fi
