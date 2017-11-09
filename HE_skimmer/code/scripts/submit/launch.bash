#!/bin/bash

job_file=$1
system=$2

max_n_jobs="`cat ../../../parameters.txt | grep max_n_jobs | awk '{print $2}'`"
user="`cat ../../../parameters.txt | grep submit_user | awk '{print $2}'`"
queue="`cat ../../../parameters.txt | grep submit_queue | awk '{print $2}'`"
skim_version="`cat ../../../parameters.txt | grep skim_version | awk '{print $2}'`"

#######################
####                  #
###   UNIGE Local    ##
##     PMO local    ###
#                  ####
#######################
if [ ${system} = "unige_local" -o ${system} = "pmo_local" ]
then
    running=`ps -ef | grep ${job_file} | grep -v 'grep' | grep -v launch | wc -l`
    if [ ${running} -eq 0  ]
    then
	njobs=`ps -ef | grep "/bin/bash ./job_" | grep -v 'grep' | wc -l`
	if [ ${njobs} -lt ${max_n_jobs} ]
	then
	    echo "INFO: Run script ${job_file} locally"
	    nohup ./${job_file} &> ${job_file}.log &
	else
	    echo "INFO: ${max_n_jobs} jobs were already submitted. Skip submission of ${job_file}..."
	fi
    elif [ ${running} -eq 1  ]
    then
	echo "INFO: Script ${job_file} was already submitted"
    else
	echo "WARNING: Script ${job_file} was submitted more than once"
    fi
######################
###                  #
##   UNIGE cluster / PBS ##
#                  ###
######################
elif [ ${system} = "unige_pbs" ] 
then

    rm -f jobs.list.tmp
    for jobid in `qstat -u ${user} | grep ${queue} | grep job_${skim_version} | grep -v ' C ' | grep -v ' E ' | awk '{print $1}' | sed -e 's/\..*//'`
    do 
	qstat -f ${jobid} >> jobs.list.tmp
    done
    running=`cat jobs.list.tmp | grep "Job_Name = ${job_file}" | wc -l`
    if [ ${running} -eq 0  ]
    then
	njobs=`qstat -u ${user} | grep ${queue} | grep job_${skim_version} | grep -v ' C ' | grep -v ' E ' | wc -l`
	if [ ${njobs} -lt ${max_n_jobs} ]
	then
	    echo "Run script ${job_file} on PBS"
	    qsub -q ${queue} -l mem=6000mb -l vmem=6000mb ${job_file}
	    #qsub -q ${queue} ${job_file}
	else
	    echo "INFO: ${max_n_jobs} jobs were already submitted. Skip submission of ${job_file}..."
	fi
    elif [ ${running} -eq 1  ]
    then
	echo "INFO: Script ${job_file} was already submitted"
    else
	echo "WARNING: Script ${job_file} was submitted more than once"
    fi

    rm -f jobs.list.tmp
######################
###                  #

#                  ###
######################

######################
###                  #
##   UNIGE cluster / SLURM ##
#                  ###
######################
elif [ ${system} = "unige_slurm" ]
then

    rm -f jobs.list.tmp
    for jobid in `squeue -u ${user} -p ${queue} | grep job_${skim_version} | grep -v ' C ' | grep -v ' E ' | awk '{print $1}' | sed -e 's/\..*//'`
    do
	qstat -f ${jobid} >> jobs.list.tmp
    done
    running=`cat jobs.list.tmp | grep "Job_Name = ${job_file}" | wc -l`
    if [ ${running} -eq 0  ]
    then
	njobs=`squeue -u ${user} -p ${queue} | grep job_${skim_version} | grep -v ' C ' | grep -v ' E ' | wc -l`
	if [ ${njobs} -lt ${max_n_jobs} ]
	then
	    echo "Run script ${job_file} on SLURM"
	    sbatch -p ${queue} --mem6000mb --workdir=$(pwd) ${job_file}
	else
	    echo "INFO: ${max_n_jobs} jobs were already submitted. Skip submission of ${job_file}..."
	fi
    elif [ ${running} -eq 1  ]
    then
	echo "INFO: Script ${job_file} was already submitted"
    else
	echo "WARNING: Script ${job_file} was submitted more than once"
    fi

    rm -f jobs.list.tmp
######################
###                  #

#                  ###
######################

elif [ ${system} = "pmo_local" ]
then
    echo ""
######################
###                  #
##    PMO cluster   ##
#                  ###
######################
elif [ ${system} = "pmo_lsf" ] 
then
    rm -f tmp.jobs
    for job in `bjobs | grep ${user} | awk '{print $1}'`
    do 
	bjobs -l ${job} | grep bash | tr '<' '\n' | tr '>' '\n' | grep bash >> tmp.jobs
    done
    running=`cat tmp.jobs | grep ${job_file} | wc -l`
    if [ ${running} -eq 0  ]
    then
	njobs=`bjobs | grep ${user} | wc -l`
	if [ ${njobs} -lt ${max_n_jobs} ]
	then
	    echo "Run script ${job_file} on LSF"
	    bsub -R "rusage[mem=6000:duration=8h]" bash ${job_file}
	    sleep 10
	else
	    echo "INFO: ${max_n_jobs} jobs were already submitted. Skip submission of ${job_file}..."
	fi
    elif [ ${running} -eq 1  ]
    then
	echo "INFO: Script ${job_file} was already submitted"
    else
	echo "WARNING: Script ${job_file} was submitted more than once"
    fi
    rm -f tmp.jobs
fi

