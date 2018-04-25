#!/bin/bash

printf "\n>>>> Execute check_files.bash \n\n"

data_location="`cat ../../parameters.txt | grep 2A_data_location | awk '{print $2}'`"
output_location="`cat ../../parameters.txt | grep output_location | awk '{print $2}'`"
year_start="`cat ../../parameters.txt | grep year_start | awk '{print $2}'`"
year_end="`cat ../../parameters.txt | grep year_end | awk '{print $2}'`"
month_start="`cat ../../parameters.txt | grep month_start | awk '{print $2}'`"
month_end="`cat ../../parameters.txt | grep month_end | awk '{print $2}'`"
day_start="`cat ../../parameters.txt | grep day_start | awk '{print $2}'`"
day_end="`cat ../../parameters.txt | grep day_end | awk '{print $2}'`"
system_type="`cat ../../parameters.txt | grep system_type | awk '{print $2}'`"
max_files="`cat ../../parameters.txt | grep max_files | awk '{print $2}'`"
files_lo=$((${max_files}-20))
files_hi=$((${max_files}+20))

source setup-externals_${system_type}.sh

release_name="`cat ../../parameters.txt | grep dampe_sw_release | awk '{print $2}'`"
release_path="`cat ../../parameters.txt | grep dampe_sw_path | awk '{print $2}'`"
echo "Set up DMPSW"
echo "cd ${release_path}/${release_name}/"
cd ${release_path}/${release_name}/
echo "source bin/thisdmpsw.sh"
source bin/thisdmpsw.sh
#source thisdmpeventclass.sh
cd - >& /dev/null

workdir="`pwd`"

for year in $(seq $year_start $year_end)
do
    for month in $(seq $month_start $month_end)
    do
	month=`printf "%02d" ${month}`
	dir="${output_location}/${year}/${month}"
	if [ ! -d ${dir} ]; then continue; fi

	cd ${dir} > /dev/null

	for day in $(seq $day_start $day_end)
	do
	    day=`printf "%02d" ${day}`
	    list="${day}.list"
            #rm -f ${list}.stats

	    printf "Checking ${output_location}/${year}/${month}/${day}... "

	    if [ ! -f ${list} ]; then 
		printf "NO DATA \n"
		continue
	    else
		printf "\n"
	    fi

	    if [ `cat ${list} | grep root | wc -l` -eq 0 ]; then continue; fi

	    nfiles=`cat ${list} | grep root | wc -l`
	    nchecked=0
	    if [ -f ${list}.stats ]
	    then
		nchecked=`cat ${list}.stats | grep root | grep -v ERROR | wc -l`
	    fi

	    if [ ${nfiles} -lt ${files_lo} ]
	    then
		printf "NOT ENOUGH FILES\n"
		continue
	    elif [ ${nfiles} -eq ${nchecked} ]
	    then
		printf "${list} is already checked\n"
	    else
		rm -f ${list}.stats 
		rm -f ${day}_data*
		ntotal_in=0
		rm -f ${list}.br
		rm -f ${list}.gr
		for f in `cat ${list}`
		do
		    printf "Check `echo ${f} | sed -e 's/.*DAMPE/DAMPE/'`... "
		    root -l -b -q "${workdir}/read_local_file.C(\"${f}\")" >& tmp
	            #cat tmp
		    n=`cat tmp | grep nentries | awk '{print $3}'`
		    if [ "${n}" = "" ]
		    then
			printf "ERROR!!! file is BAD\n"
			#cat tmp
			echo ${f} >> ${list}.br
			continue 
			#exit
		    else
			printf "OK! #events=${n}\n"
			echo ${f} >> ${list}.gr
		    fi
		    f=`echo ${f} | sed -e 's/.*releases\///'`
		    echo "${f} ${n}" >> ${list}.stats 
		    ntotal_in=`echo "${ntotal_in}+${n}" | bc`
                    #break
		done
		echo "" >> ${list}.stats 
		echo "Total number of events in data files: ${ntotal_in}" >> ${list}.stats 
		echo "" >> ${list}.stats 
	    fi

	    erange="002_010 010_025 025_050 050_100 100_500 500_000 photon"
            #erange="002_010 010_025 025_050 050_100 100_500 500_000 photon photon2"
	    for e in ${erange}
	    do
		f="${day}_data_${e}.root"
		if [ ! -f ${f} ]
		then
		    printf "${f} is not found...\n"
		    continue
		fi
		if [ -f ${f}.stats ]
		then
		    printf "${f} is already checked\n"
		else
		    printf "Check ${f}... "
		    root -l -b -q "${workdir}/read_local_file.C(\"${f}\")" >& tmp
                    #cat tmp
		    n=`cat tmp | grep nentries | awk '{print $3}'`
		    if [ "${n}" = "" ]
		    then
			printf "ERROR!!!\n"
			cat tmp
			#continue 
			exit
		    else
			printf "OK! #events=${n}\n"
		    fi
		    echo "Number of skimmed events in ${f}: ${n}" > ${f}.stats 
		fi
	    done
            #cat ${list}.stats 
            #break
	done

	rm -f tmp
	cd - > /dev/null
    done
done

echo "Create a list of output files..."
find ${output_location} | grep -v 'file_list.txt' > ${output_location}/file_list.txt
ls -l ${output_location}/file_list.txt
