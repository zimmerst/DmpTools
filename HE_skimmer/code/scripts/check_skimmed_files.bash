#!/bin/bash
delete=${1:-no}
echo ${delete}
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

	    printf "Checking ${output_location}/${year}/${month}/${day}...\n"

	    erange="002_010 010_025 025_050 050_100 100_500 500_000 photon"
            # erange="002_010 010_025 025_050 050_100 100_500 500_000 photon photon2"

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
		    RC=$?
 		    if [[ $RC != 0 ]];
		    then
 		     echo "ERROR!!! could not read local file. skip."
                     cat tmp
		     if [[ $delete == 'delete' ]];
		     then
                      echo "REQUESTED DELETION OF FILE!, YOU CAN INTERRUPT THIS BY PRESSING CTRL+C DURING THE NEXT 5 SECONDS"
		      sleep 5
		      rm -v ${f}
		     fi
                     continue
                    fi
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

