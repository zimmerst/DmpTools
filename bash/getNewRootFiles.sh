#!/usr/bin/env bash
### script to simplfiy crawling -- will create a file holding the content of the changed files on every remote site ###
indir=${1:MC}
host=$(hostname)
site=UNDEF
case $host in
     "ui03.recas.ba.infn.it") site=BARI;;
     "gridvm7.unige.ch") site=UNIGE;;
     "ui-dampe.cr.cnaf.infn.it") site=CNAF;;
    esac
output=/tmp
case $site in
  BARI)  output=/lustre/dampe/XROOTD;;
  CNAF)  output=/storage/gpfs_data/dampe/data;;
  UNIGE) output=/beegfs/dampe/prod;;
esac
target=${output}/${indir}
newfile=${output}/${indir}/${site}.new
errfile=${output}/${indir}/${site}.err
touch ${newfile}
find $(readlink -f ${target}) -mtime -1 -name "*.root" 2> ${errfile} 1> ${newfile}