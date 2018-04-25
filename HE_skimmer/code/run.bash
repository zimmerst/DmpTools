#!/bin/bash

if [ "$1" = "" ]
then
    echo ""
    echo "./run.bash first_event last_event=[-1] verbosity=[0/1/2/3] first_file last_file=[-1] output_files_tag filelist apply_cut"
    echo ""
    exit
fi

rundir="tmp_`date +%Y-%m-%d--%H-%M-%S`"
mkdir ${rundir}
pushd ${rundir}

first_event=$1 
last_event=$2 
verbosity=$3
first_file=$4 
last_file=$5
output_files_tag=$6
filelist=$7
apply_cut=$8

release_name=`cat ../makefile | grep DMPSWRELEASE | head -n1 | awk '{print $3}'`
release_path=`cat ../makefile | grep DMPSWPATH | head -n1 | awk '{print $3}'`

source setup-externals_${system_type}.sh
echo "@@@@@@@@@@@@@@@@@@@@@@@@@ Setup DMPSW"
echo "cd ${release_path}/${release_name}"
cd ${release_path}/${release_name}
echo "source bin/thisdmpsw.sh"
source bin/thisdmpsw.sh
cd - >& /dev/null
echo "@@@@@@@@@@@@@@@@@@@@@@@@@ Start processing files..."

#system_type="`cat ../parameters.txt | grep system_type | awk '{print $2}'`"
#source scripts/setup-externals_${system_type}.sh

#make clean
#make -j8

if [ `cat ../${filelist} | wc -l` -eq 0 ]
then
    echo "No files in the filelist..."
    exit
fi

rm -f progress.log
#time_start=`date +%s`
cp ../bin/main .
echo "executing: $(readlink -f main) ${first_event} ${last_event} ${verbosity} $(readlink -f ../${filelist}) ${first_file} ${last_file} ${apply_cut}"
./main ${first_event} ${last_event} ${verbosity} ../${filelist} ${first_file} ${last_file} ${apply_cut}
## catch the error code!
RC=$? 
#time_end=`date +%s`

echo ""
ls -lh data*.root
echo ""

mkdir -pv ../data/${output_files_tag}/
chmod -v 750 *
mv -v data*.root ../data/${output_files_tag}/
mv -v progress.log ../data/${output_files_tag}/

popd
rm -rfv ${rundir}

#if [[ $RC != 0 ]]; 
#then
#  echo "skimmer exited with non-zero return code: ${RC}"
#else
#  echo "skimmer exited gracefully"
#fi
#exit ${RC}
