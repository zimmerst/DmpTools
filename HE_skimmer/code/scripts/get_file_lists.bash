#!/bin/bash

printf "\n>>>> Execute get_file_lists.bash \n\n"

data_location="`cat ../../parameters.txt | grep 2A_data_location | awk '{print $2}'`"
skim_location="`cat ../../parameters.txt | grep output_location | awk '{print $2}'`"
year_start="`cat ../../parameters.txt | grep year_start | awk '{print $2}'`"
year_end="`cat ../../parameters.txt | grep year_end | awk '{print $2}'`"
month_start="`cat ../../parameters.txt | grep month_start | awk '{print $2}'`"
month_end="`cat ../../parameters.txt | grep month_end | awk '{print $2}'`"
day_start="`cat ../../parameters.txt | grep day_start | awk '{print $2}'`"
day_end="`cat ../../parameters.txt | grep day_end | awk '{print $2}'`"
system_type="`cat ../../parameters.txt | grep system_type | awk '{print $2}'`"
max_files="`cat ../../parameters.txt | grep max_files | awk '{print $2}'`"
files_lo=$((${max_files}-10))
files_hi=$((${max_files}+10))


source setup-externals_${system_type}.sh

for year in $(seq $year_start $year_end)
do
    #if [ ${year} -lt 2017 ]; then continue; fi ###### temporary !!! ####
    for month in $(seq $month_start $month_end)
    do
	month0=`printf "%02d" ${month}`
	if [ ${year} -eq 2015 -a ${month} -lt 12 ]; then continue; fi
	#if [ ${year} -gt 2016 -a ${month} -lt 2 ]; then continue; fi ###### temporary !!! ####
	for day in $(seq $day_start $day_end)
	do
	    day0=`printf "%02d" ${day}`
	    if [ ${year} -eq 2015 -a ${month} -eq 12 -a ${day} -lt 19 ]; then continue; fi
	    if [ "${year}" = "`date +%Y`" -a "${month0}" = "`date +%m`" -a "${day0}" = "`date +%d`" ]; then exit; fi 

	    printf "${year}-${month0}-${day0}: "

	    if [ ${year} -eq 2016 -a ${month} -eq 2 -a ${day} -gt 29 ]; then echo "skip"; continue; fi
	    if [ ${month} -lt 8 -a $(( ${month}%2 )) -eq 0 -a ${day} -eq 31 ]; then echo "skip"; continue; fi
	    if [ ${month} -gt 8 -a $(( ${month}%2 )) -eq 1 -a ${day} -eq 31 ]; then echo "skip"; continue; fi

	    n=-1
	    ### PMO_cluster folder
	    if [ `echo ${data_location} | grep PMO_cluster | wc -l` -eq 1 -o `echo ${data_location} | grep FlightData | wc -l` -eq 1 ]
	    then
		datadir="${data_location}/${year}${month0}${day0}"
		if [ -d ${datadir} ]
		then
		    find ${datadir} | grep -v tmp | grep -v "\.DAMPE" | grep root > list.tmp
		fi
	    ### releases folder
	    elif [ `echo ${data_location} | grep releases | wc -l` -eq 1 ]
	    then
		#find ${data_location} | grep "_${year}${month0}${day0}_" | grep root > list.tmp
	    ### FIXME!!! SZ 2017-09-05, get listing according to PMO structure 
		#find ${data_location} -name "*.root" | awk -v target="${year}${month0}${day0}" -F_ '{ts = $5; sub(/T.*/, "", ts); if (ts == target) print $0}' > list.tmp
		# these two lines are equivalent!
		find ${data_location} -name "*.root" | awk -v target="^${year}${month0}${day0}" -F_ '$5 ~ target' > list.tmp
	    ### DPM
	    elif [ `echo ${data_location} | grep dpm | wc -l` -eq 1 ]
	    then
		datadir="${data_location}/${year}${month0}${day0}"
		for d in $(xrdfs grid05.unige.ch:1094 ls ${datadir})
		do
		    rm -f list.tmp
		    xrdfs grid05.unige.ch:1094 ls ${d} | grep ".root" 1>> list.tmp
		done
            ###
	    else
		echo "ERROR: data location is non standard!"
	    fi
	    
	    if [ -f list.tmp ]
	    then
		n=`cat list.tmp | wc -l`
	    fi

	    if [ ${n} -gt -1 ]
	    then
		mkdir -p ${skim_location}/${year}/${month0}
		mv list.tmp ${skim_location}/${year}/${month0}/${day0}.list
		if [ ${n} -gt 0 ]; then printf "%d" ${n}; fi
	    fi
	    
	    if [ ${n} -gt 0 -a ${n} -lt ${files_lo} ]
	    then
		printf " NOT ENOUGH FILES\n"
	    elif [ ${n} -gt ${files_hi} ]
	    then
		printf " TOO MANY FILES\n"
	    elif [ ${n} -le 0 ]
	    then
		printf "NO DATA\n"
	    else
		printf " OK!\n"
	    fi
	done
    done
done

