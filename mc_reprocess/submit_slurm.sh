#!/bin/sh
#SBATCH --output=${WORKDIR}/%A_%a.out
#SBATCH --output=${WORKDIR}/%A_%a.err
#SBATCH --partition=mono-shared
#SBATCH --time=${STIME}
#SBATCH --mem=${SMEM}
#SBATCH --array=${SARR}
#SBATCH --export=SWPATH=${SWPATH}
#SBATCH --export=WORKDIR=${WORKDIR}
#SBATCH --export=SCRATCH=${SCRATCHDIR}
bash ${SLURM_EXEC_DIR}/wrapper.sh