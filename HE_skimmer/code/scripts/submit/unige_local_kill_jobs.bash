#!/bin/bash

printf "\n>>>> Execute unige_local_kill_jobs.bash \n\n"

pid=`ps -ef | grep '/bin/bash ./run.bash run' | grep -v 'grep' | awk '{print $2}'`
if [ "${pid}" != "" ]; then kill -9 ${pid}; fi

ps -ef | grep "/bin/bash ./job_" | grep -v 'grep'
njobs=`ps -ef | grep "/bin/bash ./job_" | grep -v 'grep' | wc -l`
if [ ${njobs} -ne 0 ]
then
    for pid in `ps -ef | grep "/bin/bash ./job_" | grep -v 'grep' | awk '{print $2}'`
    do
	echo "Kill job ${pid}"
	kill -9 ${pid}
    done
fi

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

ps -ef | grep './main' | grep -v 'grep'
njobs=`ps -ef | grep './main' | grep -v 'grep' | wc -l`
if [ ${njobs} -ne 0 ]
then
    for pid in `ps -ef | grep './main' | grep -v 'grep' | awk '{print $2}'`
    do
	echo "Kill job ${pid}"
	kill -9 ${pid}
    done
fi

rm -rfv /tmp/skimming_*


