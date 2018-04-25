#!/bin/bash

todo=$1
skim_version=$2

system_type="`cat parameters.txt | grep system_type | awk '{print $2}'`"
skim_location="`cat parameters.txt | grep output_location | awk '{print $2}'`"
year_start="`cat parameters.txt | grep year_start | awk '{print $2}'`"
year_end="`cat parameters.txt | grep year_end | awk '{print $2}'`"
month_start="`cat parameters.txt | grep month_start | awk '{print $2}'`"
month_end="`cat parameters.txt | grep month_end | awk '{print $2}'`"
day_start="`cat parameters.txt | grep day_start | awk '{print $2}'`"
day_end="`cat parameters.txt | grep day_end | awk '{print $2}'`"
user="`cat parameters.txt | grep submit_user | awk '{print $2}'`"

source code/scripts/setup-externals_${system_type}.sh

rm -f tmp

n=`ps -ef | grep '/bin/bash ./run.bash run ${skim_version}' | grep -v 'grep' | wc -l`
if [ "${todo}" = "run" -a ${n} -eq 3 ]
then
    echo "Skimmer is already running on that computer"
    exit
fi

if [ ! -d ${skim_location} ]; then mkdir -pv ${skim_location}; fi
if [ ! -d ${skim_location} ]; then 
    echo "ERROR: ${skim_location} does not exist and can not be created!"
    exit
fi

spin[0]="-"
spin[1]="\\"
spin[2]="|"
spin[3]="/"

rm -f code/scripts/submit/submit_dir/job_*bash*

pushd code
if [ "${todo}" != "kill" ]; then ./build.bash; fi
pushd scripts
pushd submit
rm -f job_*.bash
if [ "${todo}" = "kill" ]; then 
    ./${system_type}_kill_jobs.bash; 
    #rm -f ../../../tmp
    rm -rfv ${SKIMROOT}/code/scripts/submit/submit_dir/*
    exit
fi
popd
popd
popd

while [ 1 ]
do
    echo "" > nohup.out
    date
    echo "Skimmer is running on `hostname -f`"

    pushd code
    pushd scripts
    if [ "${todo}" != "kill" ]; then ./get_file_lists.bash; fi
    echo $(date)
    ./check_files.bash
    pushd submit
    if [ "${todo}" = "run" ]; then ./submit.bash submit; elif [ "${todo}" != "kill" ]; then ./submit.bash; fi
    ./${system_type}_check_jobs.bash
    popd
    echo $(date)
    ./get_summary.bash
    popd
    popd

    if [ ${system_type} = "pmo_local" -a "${todo}" = "run" ]; then ./PMO_cluster_precache.bash; fi

    if [ "${todo}" = "kill" ]; then break; fi
    if [ -f tmp ]
    then 
	if [ `cat tmp` -eq 0 ]
	then
	    if [ "${todo}" = "run" ]
	    then
		echo "Skimming is DONE!!!"
	    fi
	    break 
	fi 
    fi
    
    echo "You are viewing hohup.out, press Ctr+C to stop..."
    
    n=0
    delay=300 # seconds
    nmax=$(( 10*${delay} ))
    while [ ${n} -lt ${nmax} ]
    do
	for i in "${spin[@]}"
	do
            echo -ne "\b$i"
            sleep 0.1
	    let n++
	done
    done

done

cd code/scripts/submit/submit_dir
rm -f job_*.bash*
cd - > /dev/null

rm -f tmp

