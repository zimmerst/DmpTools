#!/bin/bash
echo ">>> executing code/scripts/submit/submit.bash "
submit=$1 
ROOTDIR_SKIM=${SKIMROOT:-../../..}
wdir=$(pwd)/submit_dir
export data_location="`cat $ROOTDIR_SKIM/parameters.txt | grep 2A_data_location | awk '{print $2}'`"
export skim_location="`cat $ROOTDIR_SKIM/parameters.txt | grep output_location | awk '{print $2}'`"
export year_start="`cat $ROOTDIR_SKIM/parameters.txt | grep year_start | awk '{print $2}'`"
export year_end="`cat $ROOTDIR_SKIM/parameters.txt | grep year_end | awk '{print $2}'`"
export month_start="`cat $ROOTDIR_SKIM/parameters.txt | grep month_start | awk '{print $2}'`"
export month_end="`cat $ROOTDIR_SKIM/parameters.txt | grep month_end | awk '{print $2}'`"
export day_start="`cat $ROOTDIR_SKIM/parameters.txt | grep day_start | awk '{print $2}'`"
export day_end="`cat $ROOTDIR_SKIM/parameters.txt | grep day_end | awk '{print $2}'`"
export start_execution_delay="`cat $ROOTDIR_SKIM/parameters.txt | grep start_execution_delay | awk '{print $2}'`"
export exec_location="`cat $ROOTDIR_SKIM/parameters.txt | grep exec_location | awk '{print $2}'`"
export file_start="`cat $ROOTDIR_SKIM/parameters.txt | grep file_start | awk '{print $2}'`"
export file_end="`cat $ROOTDIR_SKIM/parameters.txt | grep file_end | awk '{print $2}'`"
export event_start="`cat $ROOTDIR_SKIM/parameters.txt | grep event_start | awk '{print $2}'`"
export event_end="`cat $ROOTDIR_SKIM/parameters.txt | grep event_end | awk '{print $2}'`"
export apply_cut="`cat $ROOTDIR_SKIM/parameters.txt | grep apply_cut | awk '{print $2}'`"
export system_type="`cat $ROOTDIR_SKIM/parameters.txt | grep system_type | awk '{print $2}'`"
export skim_version="`cat $ROOTDIR_SKIM/parameters.txt | grep skim_version | awk '{print $2}'`"
export queue="`cat $ROOTDIR_SKIM/parameters.txt | grep queue | awk '{print $2}'`"
export max_files="`cat $ROOTDIR_SKIM/parameters.txt | grep max_files | awk '{print $2}'`"
export n_out_streams="`cat $ROOTDIR_SKIM/parameters.txt | grep n_out_streams | awk '{print $2}'`"
export files_lo=$((${max_files}-20))
export files_hi=$((${max_files}+20))

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
	    
	    if [ `ls ${skim_location}/${year}/${month}/ | grep "${day}_data" | grep -v stats | wc -l` -eq ${n_out_streams} ]; then
		printf "Data processed already\n"
		continue
	    fi

	    #job_file="submit_dir/job_${skim_version}_${year}_${month}_${day}.bash"
	    jfile="job_${skim_version}_${year}_${month}_${day}.bash"
	    job_file=$(readlink -f submit_dir/${jfile})	    
	    if [ ! -f ${job_file} ]
	    then
		printf "INFO: Create job submission file\n"	    
		cat << EOF > ${job_file}
#!/bin/bash
#SBATCH --partition=${queue}
#SBATCH --mem=1024
#SBATCH --workdir=$(readlink -f ${wdir})
#SBATCH --output=${jfile/.bash/.out}

echo "THIS IS HOST: \$(hostname)"
echo "STARTING ON: \$(date)"

exec_dir="${exec_location}"
delay=\`echo "scale=2;\${RANDOM}*${start_execution_delay}/32767" | bc\`
echo "Suspend execution by \${delay} seconds..."
sleep \${delay}

file_list="${skim_location}/${year}/${month}/${day}.list.gr"
output_dir="${skim_location}/${year}/${month}"

# OBS: was commented out SZ 2018-03-14
job_run_dir="/local/scratch/skimming___\`date +%s-%N\`"

# OBS: was default until 2018-03-14 SZ
##job_run_dir="/beegfs/dampe/tmp/HEskim/skimming___\`date +%s-%N\`"
mkdir -pv \${job_run_dir}
cd \${job_run_dir}
echo "in directory: $(readlink -f $(pwd))"
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
# UNCOMMENT FOR PHOTON2
###rsync -av data/tmp/data_photon2.root \${output_dir}/${day}_data_photon2.root
rsync -av log \${output_dir}/${day}.log

ls -lh \${output_dir}/${day}*
cd ${wdir}


rm -rf \${job_run_dir}

EOF
		chmod +x ${job_file}
	    else
		printf "INFO: Job submission file already created\n"
	    fi
	    
	    if [ "${submit}" = "submit" ]
	    then 
		nfiles=`cat ${list} | wc -l`
		if [ ${nfiles} -gt ${files_lo} -a ${nfiles} -lt ${files_hi} ]
		then
		    ./launch.bash ${job_file} ${system_type}
		elif [ ${nfiles} -lt ${files_lo} ]
		then
		    printf "NOT ENOUGH FILES\n"
		else
		    printf "TOO MANY FILES\n"
		fi
	    fi
	done
    done
done

### OBS: SZ 2018-04-12 added explict permission setter.
chmod 750 \${output_dir}
