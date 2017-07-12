#!/bin/bash

data_location="/data/PMO_cluster/2A"
cache_location="`cat parameters.txt | grep 2A_data_location | awk '{print $2}'`"
skim_location="`cat parameters.txt | grep output_location | awk '{print $2}'`"
year_start="`cat parameters.txt | grep year_start | awk '{print $2}'`"
year_end="`cat parameters.txt | grep year_end | awk '{print $2}'`"
month_start="`cat parameters.txt | grep month_start | awk '{print $2}'`"
month_end="`cat parameters.txt | grep month_end | awk '{print $2}'`"
day_start="`cat parameters.txt | grep day_start | awk '{print $2}'`"
day_end="`cat parameters.txt | grep day_end | awk '{print $2}'`"

mkdir -pv ${cache_location}/tmp/

for year in $(seq $year_start $year_end)
do
    for month in $(seq $month_start $month_end)
    do
	month0=`printf "%02d" ${month}`
	if [ ${year} -eq 2015 -a ${month} -lt 12 ]; then continue; fi
	for day in $(seq $day_start $day_end)
	do
	    day0=`printf "%02d" ${day}`
	    if [ ${year} -eq 2015 -a ${month} -eq 12 -a ${day} -lt 19 ]; then continue; fi
	    if [ "${year}" = "`date +%Y`" -a "${month0}" = "`date +%m`" -a "${day0}" = "`date +%d`" ]; then exit; fi 

	    printf "${year}-${month0}-${day0}: "

	    if [ ${year} -eq 2016 -a ${month} -eq 2 -a ${day} -gt 29 ]; then echo "skip"; continue; fi
	    if [ ${month} -lt 8 -a $(( ${month}%2 )) -eq 0 -a ${day} -eq 31 ]; then echo "skip"; continue; fi
	    if [ ${month} -gt 8 -a $(( ${month}%2 )) -eq 1 -a ${day} -eq 31 ]; then echo "skip"; continue; fi
	    
	    cache_dir="${cache_location}/${year}${month0}${day0}"
	    data_dir="${data_location}/${year}${month0}${day0}"
	    skim_dir="${skim_location}/${year}/${month0}"
            
	    if [ ! -d ${cache_dir} ]
	    then
		if [ -d ${data_dir} ]
		then
		    if [ `ps -ef | grep rsync | grep "${data_location}" | grep -v grep | wc -l` -eq 0 ]
		    then
			if [ -d ${cache_location}/tmp/${year}${month0}${day0} ]
			then

			    if [ `find ${cache_location}/tmp/${year}${month0}${day0} | grep "\.DAMPE" | wc -l` -eq 0 ]
			    then
				date >> ${cache_location}/tmp/rsync.log 
				mv ${cache_location}/tmp/${year}${month0}${day0} ${cache_location}/
				mv ${cache_location}/tmp/rsync.log ${cache_location}/
				mv ${cache_location}/rsync.log ${cache_dir}/
				printf "Data has been already pre-cached. "
			    else
				printf "Restart pre-caching of data files...\n"
				rm -v `find ${cache_location}/tmp/${year}${month0}${day0} | grep "\.DAMPE"`
				rsync -Prav ${data_dir} ${cache_location}/tmp/ &>> ${cache_location}/tmp/rsync.log &
				echo "1" > tmp
				exit				
			    fi
			else
			    printf "Pre-cache data files...\n"
			    date > ${cache_location}/tmp/rsync.log 
			    rsync -Prav ${data_dir} ${cache_location}/tmp/ &>> ${cache_location}/tmp/rsync.log &
			    echo "1" > tmp
			    exit
			fi
		    else
			printf "Pre-caching is being done at the moment...\n"
			ls -la ${cache_location}/tmp/*/*
			head -n1 ${cache_location}/tmp/rsync.log 
			date
			echo "1" > tmp
			exit
		    fi
		else
		    printf "NO DATA\n"
		fi
	    else
		printf "Data has been already pre-cached. "
	    fi

	    if [ -d ${skim_dir} ]
	    then
		processed=`find ${skim_dir} | grep -v proc | grep ${day0}_data | grep -v "\.${day0}_data" | wc -l`
	    else
		processed=0
	    fi
	    if [ ${processed} -eq 12 ]
	    then
		printf "Data has been processed already. "
		if [ ! -f ${cache_dir}/processed ]
		then
		    rm -rf ${cache_dir}/DAMPE*
		    echo "" > ${cache_dir}/processed
		fi
	    else
		printf "Data has NOT been processed yet. "
	    fi

	    printf "\n"

	done
    done
done






