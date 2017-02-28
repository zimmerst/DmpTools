#!/usr/bin/env bash
# RELIES ON $CRAWLER variable
release="latest"
infile=$1
global_badfile=$2

ofile=${infile/".txt"/".json"}
errfile=${ofile/".json"/".err"}
badfile_tmp=${ofile/".json"/".bad"}

rm -f ${errfile} ${badfile_tmp}

source /cvmfs/dampe.cern.ch/rhel6-64/etc/setup.sh
dampe_init ${release}

for f in $(cat ${infile});
do
    python ${CRAWLER_ROOT}/crawler.py ${f} -o ${ofile} 2> ${errfile}
    RC1=$?
done

python ${CRAWLER_ROOT}/analyze.py ${ofile} ${badfile_tmp} 2> ${errfile}
RC2=$?

if [ -f ${badfile_tmp} ];
then
    cat ${badfile_tmp} >> ${global_badfile}
fi

RC=$(( RC1 + RC2 ))

exit ${RC}