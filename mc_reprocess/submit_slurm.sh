#!/bin/sh
###### below is SLURM specific stuff #######
#SBATCH --output=${WORKDIR}/%A_%a.out
#SBATCH --error=${WORKDIR}/%A_%a.err
#SBATCH --partition=mono-shared
#SBATCH --time=${STIME}
#SBATCH --mem=${SMEM}
#SBATCH --array=${SARR}
export WORKDIR=${WORKDIR}
export SWPATH=${SWPATH}
export SCRATCH=${SCRATCH}
#SBATCH --export=SWPATH
#SBATCH --export=WORKDIR
#SBATCH --export=SCRATCH
bash ${SLURM_EXEC_DIR}/wrapper.sh