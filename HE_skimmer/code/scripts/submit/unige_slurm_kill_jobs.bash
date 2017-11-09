#!/bin/bash
pidtree() (
    [ -n "$ZSH_VERSION"  ] && setopt shwordsplit
    declare -A CHILDS
    while read P PP;do
        CHILDS[$PP]+=" $P"
    done < <(ps -e -o pid= -o ppid=)

    walk() {
        echo $1
        for i in ${CHILDS[$1]};do
            walk $i
        done
    }

    for i in "$@";do
        walk $i
    done
)

printf "\n>>>> Execute unige_slurm_kill_jobs.bash \n\n"

user="`cat ../../../parameters.txt | grep submit_user | awk '{print $2}'`"
queue="`cat ../../../parameters.txt | grep submit_queue | awk '{print $2}'`"
skim_version="`cat ../../../parameters.txt | grep skim_version | awk '{print $2}'`"

for job in $(squeue -u ${user} -p ${queue} | grep job_${skim_version} | grep -v " C " | awk '{print $1}' | sed -e 's/\..*//')
do 
    echo "Kill job ${job}"
    scancel ${job}
done

ps -ef | grep "/bin/bash ./run.bash run ${skim_version}" | grep -v 'grep' | grep  -v kill
njobs=`ps -ef | grep "/bin/bash ./run.bash run ${skim_version}" | grep -v 'grep' | grep -v kill | wc -l`
if [ ${njobs} -ne 0 ]
then
    for pid in `ps -ef | grep "/bin/bash ./run.bash run ${skim_version}" | grep -v 'grep' | grep -v kill | awk '{print $2}'`
    do
	echo "Kill job ${pid} and children"
	for p in $(pidtree ${pid})
	do
	    kill -9 ${p}
	done 
    done
fi
