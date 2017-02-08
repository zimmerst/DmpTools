#!/bin/bash
# this is for HPC Condor
# note that shorter intervals than 2s may be detrimental and cause premature termination of the code
export PLUGIN_NAME='hpc'
export PLUGIN_TYPE='counter'

HOSTNAME="${COLLECTD_HOSTNAME:-`hostname -f`}"
INTERVAL="${COLLECTD_INTERVAL:-15}"
CLUSTER_NAME='ettore'
USER='dampeuser'

start_run=$(date +\%s)
next_run=$((start_run+INTERVAL))
time_left=$((INTERVAL))
i=0
while [ $((time_left)) -gt 0 ];
do
        start_run=$(date +\%s)
        #echo ${start_run}
        next_run=$((start_run + INTERVAL))
        cond=$(/bin/env condor_q -name ${CLUSTER_NAME} ${USER})
        njobs=$(echo ${cond} | '{print $1}')
        pending=$(echo ${cond} | '{print $7}')
        running=$(echo ${cond} | '{print $9}')
        susp=$(echo ${cond} | '{print $11}')
        held=$(echo ${cond} | '{print $1}')
        suspend=$((held+susp))

        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-condor_pending ${start_run}:${pending:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-condor_running ${start_run}:${running:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-condor_suspend ${start_run}:${suspend:-0}"
        echo "PUTVAL ${HOSTNAME}/${PLUGIN_NAME}/${PLUGIN_TYPE}-condor_njobs ${start_run}:${njobs:-0}"
        let i++
        now=$(date +\%s)
        time_left=$((next_run - now))
        #echo "${i}: ${time_left}"
        #echo "sleep for ${time_left}"
        sleep ${time_left}

done