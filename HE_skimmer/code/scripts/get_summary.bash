#!/bin/bash

printf "\n>>>> Execute get_summary.bash \n\n"

CYA='\033[0;36m'
PUR='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m'

data_location="`cat ../../parameters.txt | grep 2A_data_location | awk '{print $2}'`"
skim_location="`cat ../../parameters.txt | grep output_location | awk '{print $2}'`"
year_start="`cat ../../parameters.txt | grep year_start | awk '{print $2}'`"
year_end="`cat ../../parameters.txt | grep year_end | awk '{print $2}'`"
month_start="`cat ../../parameters.txt | grep month_start | awk '{print $2}'`"
month_end="`cat ../../parameters.txt | grep month_end | awk '{print $2}'`"
day_start="`cat ../../parameters.txt | grep day_start | awk '{print $2}'`"
day_end="`cat ../../parameters.txt | grep day_end | awk '{print $2}'`"
system_type="`cat ../../parameters.txt | grep system_type | awk '{print $2}'`"
n_out_streams="`cat ../../parameters.txt | grep n_out_streams | awk '{print $2}'`"
max_file="`cat ../../parameters.txt | grep max_files | awk '{print $2}'`"

source setup-externals_${system_type}.sh

echo ""  > ${skim_location}/summary.txt

printf "\n Color legend:\n" | tee -a ${skim_location}/summary.txt
printf "  ${RED}Files are NOT skimmed${NC}\n" | tee -a ${skim_location}/summary.txt
printf "  ${CYA}Files are skimmed${NC}\n" | tee -a ${skim_location}/summary.txt
printf "  ${PUR}Number of events is less then expected${NC}\n\n" | tee -a ${skim_location}/summary.txt

for year in $(seq $year_start $year_end)
do
    for month in $(seq $month_start $month_end)
    do
	month=`printf "%02d" ${month}`
	dir="${skim_location}/${year}/${month}"
	if [ ! -d ${dir} ]; then continue; fi

	printf "%10s.%-10s\n" ${month} ${year}
	printf "%10s.%-10s\n" ${month} ${year} >> ${skim_location}/summary.txt

	printf "%10s" "day"
	printf "%10s" "day" >> ${skim_location}/summary.txt
	for day in $(seq $day_start $day_end)
	do
	    printf "%6d" ${day}
	    printf "%6d" ${day} >> ${skim_location}/summary.txt
	done
	printf "\n"
	printf "\n" >> ${skim_location}/summary.txt

	printf "%10s" "#files"
	printf "%10s" "#files" >> ${skim_location}/summary.txt
	for day in $(seq $day_start $day_end)
	do
	    day=`printf "%02d" ${day}`
	    if [ -f ${dir}/${day}.list ]
	    then
		nfiles=`cat ${dir}/${day}.list | grep root | wc -l`
		processed=`find ${dir} | grep -v proc | grep ${day}_data | grep -v "\.${day}_data" | grep -v stats | wc -l`
		if [ ${nfiles} -eq 0 ]
		then
		    printf "%6d" 0 
		    printf "%6d" 0  >> ${skim_location}/summary.txt
		elif [ ${nfiles} -lt $((${max_files}-10)) -o ${nfiles} -gt $((${max_files}+10)) ]
		then
		    printf "${PUR}%6d${NC}" ${nfiles} 
		    printf "${PUR}%6d${NC}" ${nfiles}  >> ${skim_location}/summary.txt		
		else
		    if [ ${processed} -eq ${n_out_streams} ]
		    then
			printf "${CYA}%6d${NC}" ${nfiles} 
			printf "${CYA}%6d${NC}" ${nfiles}  >> ${skim_location}/summary.txt
			nfiles_processed=`cat ${dir}/${day}.log | grep TChain | grep root | wc -l`
			if [ ${nfiles_processed} -gt ${nfiles} ]
			then
			    printf "*"
			fi
		    else
			printf "${RED}%6d${NC}" ${nfiles} 
			printf "${RED}%6d${NC}" ${nfiles}  >> ${skim_location}/summary.txt
		    fi
		fi
	    else
		printf "%6d" 0 
		printf "%6d" 0   >> ${skim_location}/summary.txt
	    fi
	done
	
	
	printf "\n%10s" "#events"
	printf "\n%10s" "#events" >> ${skim_location}/summary.txt
	for day in $(seq $day_start $day_end)
	do
	    day=`printf "%02d" ${day}`
	    if [ -f ${dir}/${day}.list ]
	    then
		nfiles=`cat ${dir}/${day}.list | grep root | wc -l`
		processed=`find ${dir} | grep -v proc | grep ${day}_data | grep -v "\.${day}_data" | grep -v stats | wc -l`
		if [ -f ${dir}/${day}.list.stats ]
		then
		    n0=`cat ${dir}/${day}.list.stats | grep Total | awk '{print $8}'`
		    n=`echo "scale=1; ${n0}/1000000.0" | bc`
		else
		    n0=0
		    n=0
		fi
		if [ ${nfiles} -eq 0 ]
		then
		    printf "%6.1f" 0
		    printf "%6.1f" 0 >> ${skim_location}/summary.txt
		else
		    if [ ${n0} -lt 4000000 -o ${n0} -gt 5300000 ]
		    then
			printf "${PUR}%6s${NC}" "${n}M"
			printf "${PUR}%6s${NC}" "${n}M" >> ${skim_location}/summary.txt
		    elif [ ${processed} -eq ${n_out_streams} ]
		    then
			printf "${CYA}%6s${NC}" "${n}M"
			printf "${CYA}%6s${NC}" "${n}M" >> ${skim_location}/summary.txt
		    else
			printf "${RED}%6s${NC}" "${n}M"
			printf "${RED}%6s${NC}" "${n}M" >> ${skim_location}/summary.txt
		    fi
		fi
	    else
		printf "%6.1f" 0
		printf "%6.1f" 0 >> ${skim_location}/summary.txt
	    fi
	done


	erange="002_010 010_025 025_050 050_100 100_500 500_000 photon"
	for e in ${erange}
	do
	    printf "\n%10s" "${e}"
	    printf "\n%10s" "${e}" >> ${skim_location}/summary.txt
	    for day in $(seq $day_start $day_end)
	    do
		day=`printf "%02d" ${day}`
		if [ -f ${dir}/${day}.list ]
		then 
		    nfiles=`cat ${dir}/${day}.list | grep root | wc -l`
		    processed=`find ${dir} | grep -v proc | grep ${day}_data_${e}.root | grep -v stats | grep -v "\.${day}_data" | wc -l`
		    if [ ${nfiles} -eq 0 ]
		    then
		    printf "%6.1d" 0 
		    printf "%6.1d" 0  >> ${skim_location}/summary.txt
		    else
			if [ ${processed} -eq 1 -a -f ${dir}/${day}_data_${e}.root.stats ]
			then
			    n0=`cat ${dir}/${day}_data_${e}.root.stats | awk '{print $7}'`
			    n=`echo "scale=0; ${n0}/1000.0" | bc`
			    
			    CYA0=${CYA}
			    not_enough_events=0
			    
			    if [ "${e}" = "002_010" -a ${n0} -lt 12500 ]; then CYA=${PUR}; not_enough_events=1; fi
			    if [ "${e}" = "010_025" -a ${n0} -lt 14000 ]; then CYA=${PUR}; not_enough_events=1; fi
			    if [ "${e}" = "025_050" -a ${n0} -lt  2000 ]; then CYA=${PUR}; not_enough_events=1; fi
			    if [ "${e}" = "050_100" -a ${n0} -lt   800 ]; then CYA=${PUR}; not_enough_events=1; fi
			    if [ "${e}" = "100_500" -a ${n0} -lt   350 ]; then CYA=${PUR}; not_enough_events=1; fi
			    if [ "${e}" = "500_000" -a ${n0} -lt    20 ]; then CYA=${PUR}; not_enough_events=1; fi
			    if [ "${e}" = "photon" -a ${n0}  -lt 100000 ]; then CYA=${PUR}; not_enough_events=1; fi
                            if [ "${e}" = "002_010" -o "${e}" = "photon" ]; 
			    then 
				n0=`echo "scale=0; ${n0}/1000.0" | bc`
                                printf "${CYA}%6s${NC}" "${n0}k"
                                printf "${CYA}%6s${NC}" "${n0}k" >> ${skim_location}/summary.txt
			    else
			        printf "${CYA}%6d${NC}" ${n0} 
			        printf "${CYA}%6d${NC}" ${n0}  >> ${skim_location}/summary.txt
			    fi
			    CYA=${CYA0}
			else
			    printf "${RED}%6d${NC}" 0
			    printf "${RED}%6d${NC}" 0 >> ${skim_location}/summary.txt
			fi
		    fi
		else
		    printf "%6d" 0 
		    printf "%6d" 0 >> ${skim_location}/summary.txt
		fi
	    done
	done

	printf "\n\n"
	printf "\n\n" >> ${skim_location}/summary.txt
    done
done

./make_summary_plot.bash "-l -b -q"
