#!/bin/bash

submit=$1 

data_location="`cat ../../../parameters.txt | grep 2A_data_location | awk '{print $2}'`"
skim_location="`cat ../../../parameters.txt | grep output_location | awk '{print $2}'`"
year_start="`cat ../../../parameters.txt | grep year_start | awk '{print $2}'`"
year_end="`cat ../../../parameters.txt | grep year_end | awk '{print $2}'`"
month_start="`cat ../../../parameters.txt | grep month_start | awk '{print $2}'`"
month_end="`cat ../../../parameters.txt | grep month_end | awk '{print $2}'`"
day_start="`cat ../../../parameters.txt | grep day_start | awk '{print $2}'`"
day_end="`cat ../../../parameters.txt | grep day_end | awk '{print $2}'`"
start_execution_delay="`cat ../../../parameters.txt | grep start_execution_delay | awk '{print $2}'`"
exec_location="`cat ../../../parameters.txt | grep exec_location | awk '{print $2}'`"
file_start="`cat ../../../parameters.txt | grep file_start | awk '{print $2}'`"
file_end="`cat ../../../parameters.txt | grep file_end | awk '{print $2}'`"
event_start="`cat ../../../parameters.txt | grep event_start | awk '{print $2}'`"
event_end="`cat ../../../parameters.txt | grep event_end | awk '{print $2}'`"
apply_cut="`cat ../../../parameters.txt | grep apply_cut | awk '{print $2}'`"
system_type="`cat ../../../parameters.txt | grep system_type | awk '{print $2}'`"
skim_version="`cat ../../../parameters.txt | grep skim_version | awk '{print $2}'`"

for year in $(seq $year_start $year_end)
do
    for month in $(seq $month_start $month_end)
    do
	month=`printf "%02d" ${month}`
	dir="${skim_location}/${year}/${month}"
	if [ ! -d ${dir} ]; then continue; fi
	
	for day in $(seq $day_start $day_end)
	do
	    day=`printf "%02d" ${day}`
	    
	    if [ "${year}" = "`date +%Y`" -a "${month}" = "`date +%m`" -a "${day}" = "`date +%d`" ]; then exit; fi 
	    
	    list="${skim_location}/${year}/${month}/${day}.list.gr"

	    printf "${year}/${month}/${day}: "
	    
	    if [ ! -f ${list} ]; then 
		printf "NO DATA\n"
		continue
	    fi
	    
	    if [ `ls ${skim_location}/${year}/${month}/ | grep "${day}_data" | grep -v stats | wc -l` -eq 6 ]; then
		printf "Data processed already\n"
		continue
	    fi

	    job_file="job_${skim_version}_${year}_${month}_${day}.bash"
	    
	    if [ ! -f ${job_file} ]
	    then
		printf "INFO: Create job submission file\n"	    
		cat << EOF > ${job_file}
#!/bin/bash

delay=\`echo "scale=2;\${RANDOM}*${start_execution_delay}/32767" | bc\`
echo "Suspend execution by \${delay} seconds..."
sleep \${delay}

file_list="${skim_location}/${year}/${month}/${day}.list.gr"
output_dir="${skim_location}/${year}/${month}"

job_run_dir="/tmp/skimming___\`date +%s-%N\`"
mkdir -pv \${job_run_dir}
pushd \${job_run_dir}

exec_dir="${exec_location}"
mkdir -pv bin
cp -v \${exec_dir}/scripts/setup-externals_${system_type}.sh .
cp -v \${exec_dir}/bin/main bin/
cp -v \${exec_dir}/makefile .
cp -v \${exec_dir}/run.bash .
cp -v \${file_list} file_list.txt
source setup-externals_${system_type}.sh
./run.bash ${event_start} ${event_end} 0 ${file_start} ${file_end} tmp file_list.txt ${apply_cut} &> log 

rsync -av data/tmp/data_002_010.root \${output_dir}/${day}_data_002_010.root
rsync -av data/tmp/data_010_025.root \${output_dir}/${day}_data_010_025.root
rsync -av data/tmp/data_025_050.root \${output_dir}/${day}_data_025_050.root
rsync -av data/tmp/data_050_100.root \${output_dir}/${day}_data_050_100.root
rsync -av data/tmp/data_100_500.root \${output_dir}/${day}_data_100_500.root
rsync -av data/tmp/data_500_000.root \${output_dir}/${day}_data_500_000.root
rsync -av data/tmp/data_photon.root \${output_dir}/${day}_data_photon.root
rsync -av log \${output_dir}/${day}.log

ls -lh \${output_dir}/${day}*

popd

rm -rf \${job_run_dir}

EOF
		chmod +x ${job_file}
	    else
		printf "INFO: Job submission file already created\n"
	    fi
	    
	    if [ "${submit}" = "submit" ]
	    then 
		nfiles=`cat ${list} | wc -l`
		if [ ${nfiles} -gt 29 -a ${nfiles} -lt 32 ]
		then
		    ./launch.bash ${job_file} ${system_type}
		elif [ ${nfiles} -lt 30 ]
		then
		    printf "NOT ENOUGH FILES\n"
		else
		    printf "TOO MANY FILES\n"
		fi
	    fi
	done
    done
done
