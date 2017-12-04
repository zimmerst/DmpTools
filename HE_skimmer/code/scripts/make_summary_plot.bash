#!/bin/bash

param="${1}"

printf "\n>>>> Execute make_summary_plot.bash \n\n"

rm -f raw_summary.txt

stop=0

data_location="`cat ../../parameters.txt | grep 2A_data_location | awk '{print $2}'`"
skim_location="`cat ../../parameters.txt | grep output_location | awk '{print $2}'`"
year_start="`cat ../../parameters.txt | grep year_start | awk '{print $2}'`"
year_end="`cat ../../parameters.txt | grep year_end | awk '{print $2}'`"
month_start="`cat ../../parameters.txt | grep month_start | awk '{print $2}'`"
month_end="`cat ../../parameters.txt | grep month_end | awk '{print $2}'`"
day_start="`cat ../../parameters.txt | grep day_start | awk '{print $2}'`"
day_end="`cat ../../parameters.txt | grep day_end | awk '{print $2}'`"
system_type="`cat ../../parameters.txt | grep system_type | awk '{print $2}'`"

source setup-externals_${system_type}.sh

for year in $(seq $year_start $year_end)
do
    for month in $(seq $month_start $month_end)
    do
	month0=`printf "%02d" ${month}`
	if [ ${year} -eq 2015 -a ${month} -lt 12 ]; then continue; fi
	for day in $(seq $day_start $day_end)
	do
	    if [ ${stop} -eq 1 ]; then break; fi
	    day0=`printf "%02d" ${day}`
	    if [ ${year} -eq 2015 -a ${month} -eq 12 -a ${day} -lt 26 ]; then continue; fi
	    if [ "${year}" = "`date +%Y`" -a "${month0}" = "`date +%m`" -a "${day0}" = "`date +%d`" ]; 
	    then stop=1; fi 

	    #printf "${year}-${month0}-${day0}: "	    
	    
	    if [ ${year} -eq 2016 -a ${month} -eq 2 -a ${day} -gt 29 ]; then #echo "skip"; 
		continue; fi
	    if [ ${month} -lt 8 -a $(( ${month}%2 )) -eq 0 -a ${day} -eq 31 ]; then #echo "skip"; 
		continue; fi
	    if [ ${month} -gt 8 -a $(( ${month}%2 )) -eq 1 -a ${day} -eq 31 ]; then #echo "skip"; 
		continue; fi
	    
	    f_in="${skim_location}/${year}/${month0}/${day0}.list.stats"
	    f_out_1="${skim_location}/${year}/${month0}/${day0}_data_002_010.root.stats"
	    f_out_2="${skim_location}/${year}/${month0}/${day0}_data_010_025.root.stats"
	    f_out_3="${skim_location}/${year}/${month0}/${day0}_data_025_050.root.stats"
	    f_out_4="${skim_location}/${year}/${month0}/${day0}_data_050_100.root.stats"
	    f_out_5="${skim_location}/${year}/${month0}/${day0}_data_100_500.root.stats"
	    f_out_6="${skim_location}/${year}/${month0}/${day0}_data_500_000.root.stats"
	    f_out_7="${skim_location}/${year}/${month0}/${day0}_data_photon.root.stats"
            #f_out_8="${skim_location}/${year}/${month0}/${day0}_data_photon2.root.stats" # UNCOMMENT FOR PHOTON2

	    if [ -f ${f_in} ]
	    then
		n1=`cat ${f_in} | grep Total | awk '{print $8}'`
		n2=`cat ${f_in} | grep root | wc -l`
		if [ -f ${f_out_1} ]; then n3=`cat ${f_out_1} | awk '{print $7}'`; else n3=0; fi
		if [ -f ${f_out_2} ]; then n4=`cat ${f_out_2} | awk '{print $7}'`; else n4=0; fi
		if [ -f ${f_out_3} ]; then n5=`cat ${f_out_3} | awk '{print $7}'`; else n5=0; fi
		if [ -f ${f_out_4} ]; then n6=`cat ${f_out_4} | awk '{print $7}'`; else n6=0; fi
		if [ -f ${f_out_5} ]; then n7=`cat ${f_out_5} | awk '{print $7}'`; else n7=0; fi
		if [ -f ${f_out_6} ]; then n8=`cat ${f_out_6} | awk '{print $7}'`; else n8=0; fi
		if [ -f ${f_out_7} ]; then n8=`cat ${f_out_7} | awk '{print $7}'`; else n9=0; fi
                #if [ -f ${f_out_8} ]; then n9=`cat ${f_out_8} | awk '{print $7}'`; else n10=0; fi # UNCOMMENT FOR PHOTON2
	    else
		n1=0
		n2=0
		n3=0
		n4=0
		n5=0
		n6=0
		n7=0
		n8=0
		n9=0
                #n10=0
	    fi
	    echo "${n1} in ${n2} files"

	    echo "${year} ${month} ${day} ${n1} ${n2} ${n3} ${n4} ${n5} ${n6} ${n7} ${n8} ${n9}" >> raw_summary.txt
            #echo "${year} ${month} ${day} ${n1} ${n2} ${n3} ${n4} ${n5} ${n6} ${n7} ${n8} ${n9} ${n10}" >> raw_summary.txt  # UNCOMMENT FOR PHOTON2
	done
    done
done

ndays=`cat raw_summary.txt | wc -l`

root ${param} "plot_summary.C(${ndays})"

#root ${param} "plot_summary.C(${year_start},${month_start},${day_start},${ndays})"

