#!/bin/bash

spin[0]="-"
spin[1]="\\"
spin[2]="|"
spin[3]="/"

while [ 1 ]
do 
    /atlas/software/batch-tools/get-job-meminfo.py | grep russlan
    echo "**************************"
    n=0
    delay=30 # seconds
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

