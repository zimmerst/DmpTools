#!/bin/bash
# this is for the SLURM batch system
# note that shorter intervals than 2s may be detrimental and cause premature termination of the code
export PLUGIN_NAME='hpc'
export PLUGIN_TYPE='counter'

HOSTNAME="${COLLECTD_HOSTNAME:-`hostname -f`}"
INTERVAL="${COLLECTD_INTERVAL:-15}"
USERNAME="${USER:-zimmers}"
interval=${INTERVAL%.*}
start_run=$(date +\%s)
next_run=$((start_run+interval))
time_left=$((interval))
i=0
while [ $((time_left)) -gt 0 ];
do
        tmpfile=/tmp/${EXPERIMENT}.squeue
        start_run=$(date +\%s)
        #echo ${start_run}
        next_run=$((start_run + interval))

        /bin/env squeue -u ${USERNAME} -t "PD,R,Suspended,CD,F" | sed /"NODELIST"/d > ${tmpfile}

        njobs=$(grep -c ${USERNAME} ${tmpfile})
        pending=$(grep -c "PD" ${tmpfile})
        running=$(grep -c "R" ${tmpfile})
        suspend=$(grep -c "Suspended" ${tmpfile})
        completed=$(grep -c "CD" ${tmpfile})
        failed=$(grep -c "F" ${tmpfile})

        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-slurm_pending ${start_run}:${pending:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-slurm_running ${start_run}:${running:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-slurm_suspend ${start_run}:${suspend:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-slurm_completed ${start_run}:${completed:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-slurm_failed ${start_run}:${failed:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-slurm_njobs ${start_run}:${njobs:-0}"
        rm -f ${tmpfile}
        let i++
        now=$(date +\%s)
        time_left=$((next_run - now))
        #echo "${i}: ${time_left}"
        #echo "sleep for ${time_left}"
        sleep ${time_left}

done