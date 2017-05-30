#!/bin/sh
#SBATCH --output=${WORKDIR}/%A_%a.out
#SBATCH --output=${WORKDIR}/%A_%a.err
#SBATCH --partition=mono-shared
#SBATCH --time=${STIME}
#SBATCH --mem=${SMEM}
#SBATCH --array=${SARR}
bash ${SLURM_EXEC_DIR}/wrapper.sh