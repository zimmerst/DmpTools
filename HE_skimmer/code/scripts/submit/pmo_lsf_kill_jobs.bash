#!/bin/bash

printf "\n>>>> Execute pmo_lsf_kill_jobs.bash \n\n"

bkill 0

ps -ef | grep '/bin/bash ./run.bash' | grep -v 'grep' | grep  -v kill
njobs=`ps -ef | grep '/bin/bash ./run.bash' | grep -v 'grep' | grep -v kill | wc -l`
if [ ${njobs} -ne 0 ]
then
    for pid in `ps -ef | grep '/bin/bash ./run.bash' | grep -v 'grep' | grep -v kill | awk '{print $2}'`
    do
	echo "Kill job ${pid}"
	kill -9 ${pid}
    done
fi

