#!/bin/bash

#SBATCH --mem=10000
#SBATCH --time=2-0:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=4     
#SBATCH --output=/work/slater_lab/shared_slurm_outs/RNAseq/reads_aggregator-%j.out                                                                                                                                                                          

echo "Job started: "$(date)

# DEPOSIT_DIR, COMPUTE_HOME, and N_SAMPLES are environment
# variables that are defined previously in RNAseq.slurm.

# Source required python script.
cd $COMPUTE_HOME
cp /work/slater_lab/shared_compute_scripts/reads_aggregator.py .
# Enter virtual environment.
source /work/slater_lab/anaconda3/bin/activate ml

# Execute python script.
python reads_aggregator.py $DEPOSIT_DIR $N_SAMPLES

# Perform cleanup.
conda deactivate
rm reads_aggregator.py
rm $DEPOSIT_DIR/fastqs/*.fastq

# Set appropriate permissions for all contents in the deposit dir.
chgrp -R slater_lab $DEPOSIT_DIR
find $DEPOSIT_DIR -type d | xargs chmod 2770
find $DEPOSIT_DIR -type f | xargs chmod 660

echo "Job complete: "$(date)
