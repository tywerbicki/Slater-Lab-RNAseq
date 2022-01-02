#!/bin/bash

#SBATCH --mem=50000
#SBATCH --time=0-6:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16    
#SBATCH --output=/work/slater_lab/shared_slurm_outs/RNAseq/qc_STAR_align-%j.out                                                                                                                                                                            

echo "Job started: "$(date)

# DEPOSIT_DIR, STAR_DIR, READ1_PATH, READ2_PATH, and GENOME_DIR 
# are environment variables that are defined previously in RNAseq.slurm.

module purge
module load biobuilds/2017.11

cd $DEPOSIT_DIR/fastqs
# Perform quality checks for sample.
fastqc $READ1_PATH $READ2_PATH \
     --outdir=$DEPOSIT_DIR/fastqs/quality_assessment/

echo "Quality assessment complete: "$(date)

cd $STAR_DIR
# Perform STAR alignment.
STAR --runThreadN $SLURM_NTASKS \
     --genomeDir $GENOME_DIR \
     --outSAMtype BAM SortedByCoordinate \
     --quantMode GeneCounts \
     --readFilesIn $READ1_PATH $READ2_PATH

# Flag to communicate that alignment is complete.
touch DONE.txt

echo "STAR alignment complete: "$(date)
