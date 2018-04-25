#!/bin/bash
version=v2
out=/beegfs/dampe/prod/FM/skim/6.0.0
mon(){
  #nodes=$(sinfo --N -h | awk '{print $1}' | uniq | wc -l)
  cpus=$(scontrol show partition debug | grep TotalCPUs | awk '{print $2}' | awk -F= '{print $2}')
  days=$(find ${out}/${version} -name "*.list" | wc -l)
  good_days=$(find ${out}/${version} -name "*.list.gr" | wc -l)
  npd=$(squeue -u dampe_prod -h -t PD | grep ${version} | wc -l)
  nr=$(squeue -u dampe_prod -h -t R | grep ${version} | wc -l)
  echo "$(date): days: ${good_days}/${days}  jobs (CPUs/running/pending): ${cpus}/${nr}/${npd}"
}
echo "interrupt with Ctrl+C"
while true;
do
 mon
 sleep 300
done
