#!/bin/bash
# this is for HPC Condor
# note that shorter intervals than 2s may be detrimental and cause premature termination of the code
export PLUGIN_NAME='hpc'
export PLUGIN_TYPE='counter'

HOSTNAME="${COLLECTD_HOSTNAME:-`hostname -f`}"
INTERVAL="${COLLECTD_INTERVAL:-15}"
CLUSTER_NAME='ettore'
USER='dampeuser'
interval=${INTERVAL%.*}
start_run=$(date +\%s)
next_run=$((start_run+interval))
time_left=$((interval))
i=0
while [ $((time_left)) -gt 0 ];
do
        start_run=$(date +\%s)
        #echo ${start_run}
        next_run=$((start_run + interval))
        cond=$(/bin/env condor_q -name ${CLUSTER_NAME} ${USER} | tail -n 1)
        njobs=$(echo ${cond} | awk '{print $1}')
        comp=$(echo ${cond} | awk '{print $3}')
        removed=$(echo ${cond} | awk '{print $5}')
        pending=$(echo ${cond} | awk '{print $7}')
        running=$(echo ${cond} | awk '{print $9}')
        susp=$(echo ${cond} | awk '{print $11}')
        held=$(echo ${cond} | awk '{print $13}')

        suspend=$((${held%.*}+${susp%.*}))
        completed=$((${comp%.*}+${removed%.*}))

        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-condor_pending ${start_run}:${pending:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-condor_running ${start_run}:${running:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-condor_suspend ${start_run}:${suspend:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-condor_completed ${start_run}:${completed:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-condor_njobs ${start_run}:${njobs:-0}"

        let i++
        now=$(date +\%s)
        time_left=$((next_run - now))
        #echo "${i}: ${time_left}"
        #echo "sleep for ${time_left}"
        sleep ${time_left}

done