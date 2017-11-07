#!/bin/bash
wd=$(pwd)
RUNTIME=$1
waved=/home/sysuser/CAEN/WaveDumpAnalysis/WaveDump
rm -f syslog.txt
s="$(date): starting overnight operations - unattended - this script will run as infinite loop, press Q to exit"
echo ${s} >> syslog.txt
echo ${s}
i=0
killme=false
while true;
do
    if ${killme};
    then
    	break
    fi
    for thresh in HIGH LOW;
    do
	echo "$(date): entering ${thresh} cycle ${i}"
	echo "REMINDER: Press Q to exit. "
	read -t 0.25 -N 1 input
	if [[ $input = "q" ]] || [[ $input = "Q" ]]; then
        # The following line is for the prompt to appear on a new line.
	    s="$(date): requested end of loop"
	    echo ${s}
	    echo ${s} >> syslog.txt
	    killme=true
	    break
	fi
	echo "$(date): start calibrations"
	python startCalibRaw2.py 1>${wd}/calib.log 2>${wd}/calib.err
	echo "$(date): start data run for ${RUNTIME} seconds."
        ### 5400 = 90*60 seconds
	rm -f ${wd}/daq.log ${wd}/daq.err
	python startDaqRaw2.py $(( RUNTIME + 30 )) 1>${wd}/daq.log 2>${wd}/daq.err &
	daq_pid=$!
	echo "DAQ PID: ${daq_pid}"
        ####
        ### DO NOT CHANGE A SINGLE THING IN THE CODE BELOW - UNLESS YOU ABSOLUTELY KNOW WHAT YOU ARE DOING"
        ### Triggers ###
	cd ${waved}/fADC_3
	rm -f /tmp/fADC_3_FIFO
	mkfifo /tmp/fADC_3_FIFO
	touch WaveDump.out WaveDump.err
	WaveDump WaveDump.conf 1> ${waved}/fADC_3/WaveDump.out 2> ${waved}/fADC_3/WaveDump.err < /tmp/fADC_3_FIFO &
	echo -n . > /tmp/fADC_3_FIFO
	echo -n s > /tmp/fADC_3_FIFO
	echo -n W > /tmp/fADC_3_FIFO
	echo -n P > /tmp/fADC_3_FIFO

	cd ${waved}/fADC_2
	touch WaveDump.out WaveDump.err
	if [ "${thresh}" = "LOW" ];
	then
	    echo "Threshold is LOW - activating fADC_2"
	    rm -f /tmp/fADC_2_FIFO
	    mkfifo /tmp/fADC_2_FIFO
	    WaveDump WaveDump.conf 1> ${waved}/fADC_2/WaveDump.out 2> ${waved}/fADC_2/WaveDump.err < /tmp/fADC_2_FIFO &
	    echo -n . > /tmp/fADC_2_FIFO
	    echo -n s > /tmp/fADC_2_FIFO
	fi

	cd ${waved}/fADC_1
	touch WaveDump.out WaveDump.err
	rm -f /tmp/fADC_1_FIFO
	mkfifo /tmp/fADC_1_FIFO
	WaveDump WaveDump_${thresh}.conf 1> ${waved}/fADC_1/WaveDump.out 2> ${waved}/fADC_1/WaveDump.err < /tmp/fADC_1_FIFO &
	echo -n . > /tmp/fADC_1_FIFO
	echo -n s > /tmp/fADC_1_FIFO

        # RUN for 90 minutes
	sleep ${RUNTIME}
        # STOP TRIGGERS
	echo -n s > /tmp/fADC_1_FIFO
	echo -n q > /tmp/fADC_1_FIFO
	if [ "${thresh}" = "LOW" ];
	then
	    echo "Threshold is LOW - activating fADC_2"
	    ### low uses fADC_2, HIGH does not!
	    echo -n s > /tmp/fADC_2_FIFO
	    echo -n q > /tmp/fADC_2_FIFO
	fi
	echo -n W > /tmp/fADC_3_FIFO
	echo -n s > /tmp/fADC_3_FIFO
	echo -n q > /tmp/fADC_3_FIFO
	#echo "DEBUG:: working directory ${wd}"
	DIR=/proc/${daq_pid}
	while [ -d ${DIR} ];
	do
	    echo "$(date): runDAQ still running ${daq_pid}, try again in 10 secs"
	    sleep 10
	done
	echo "$(date): runDAQ finished - cleaning house..."

	run_number=$(grep "next data run will be :" ${wd}/daq.log | awk '{print $7}')
	echo "RUN NUMBER: ${run_number}"
	daq_file=$(grep "DAQ file: " ${wd}/daq.log | awk '{print $3}')
	#echo "DEBUG:: DAQ FILE: ${daq_file}"
	run_dir=$(dirname ${daq_file})
	#echo "DEBUG:: RUN DIR: ${run_dir}"
	mkdir -pv ${run_dir}/fADC_3
	find ${waved}/fADC_3 -name "wave*.txt" | sed /backup/d | xargs -I @ mv -vf @ ${run_dir}/fADC_3/.
	echo ${thresh} > ${run_dir}/thresholds
	echo "dispatching analysis script"
	bash ${wd}/analyze.sh ${run_dir} 1> ${run_dir}/logs/analyze.out 2> ${run_dir}/logs/analyze.err &
	echo "copy log files to run dir"
	mkdir -pv ${run_dir}/logs
	mv -vf ${wd}/daq.* ${run_dir}/logs/.
	mv -vf ${wd}/calib.* ${run_dir}/logs/.
	for f in fADC_1 fADC_2 fADC_3;
	do
	    mv -fv ${waved}/${f}/WaveDump.out ${run_dir}/logs/WaveDump_${f}.out
	    mv -fv ${waved}/${f}/WaveDump.err ${run_dir}/logs/WaveDump_${f}.err
	done
	let i++
	echo "sleep for 30s for next run, do not push any buttons..."
	sleep 30
	cd ${wd}
    done
done

echo "$(date) done operations"