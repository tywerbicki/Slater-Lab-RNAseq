#!/bin/bash

#SBATCH --mem=150000
#SBATCH --time=0-12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=40
#SBATCH --output=/work/slater_lab/shared_slurm_outs/RNAseq/RNAseq-%j.out

echo "Job started: "$(date)
echo -e "CPUS available to job: "${SLURM_JOB_CPUS_PER_NODE}"\n"

##### Specify user-defined program parameters. #####
export COMPUTE_HOME=$HOME/compute_scripts
SLURM_HOME=$HOME/slurm_scripts
TARGET_DIR=/work/slater_lab/data/AOF-Maternal-Blood-RNAseq
export DEPOSIT_DIR=/scratch/${SLURM_JOB_ID}/AOF_RNAseq_$USER
export N_SAMPLES=$(find $TARGET_DIR -mindepth 1 -maxdepth 1 -type d | wc -l)
N_LANES=4
export GENOME_DIR=/work/slater_lab/genomes/human_genome

# Check user-defined parameters for validity.
function check_dir() {
    if [[ $1 == "exist" ]]; then
        [[ ! -d "$2" ]] && echo "ERROR: ""$2"" is not an existing directory." && exit 1
    elif [[ $1 == "not_exist" ]]; then
        [[ -d "$2" ]] && echo "ERROR: ""$2"" is an existing directory." && exit 1
    else
        echo "ERROR: check_dir expecting 'exist' | 'not_exist' for \$1. " && exit 1
    fi
}

check_dir "exist" $COMPUTE_HOME
check_dir "exist" $SLURM_HOME
check_dir "exist" $TARGET_DIR
check_dir "not_exist" $DEPOSIT_DIR
check_dir "exist" $GENOME_DIR

[[ $N_SAMPLES -lt "1" ]] && echo "ERROR: N_SAMPLES < 1." && exit 1
[[ $N_LANES -lt "1" ]] && echo "ERROR: N_LANES < 1." && exit 1

# Log user-defined parameters.
echo "User-defined parameters:"
echo "COMPUTE_HOME = "$COMPUTE_HOME
echo "SLURM_HOME = "$SLURM_HOME
echo "TARGET_DIR = "$TARGET_DIR
echo "DEPOSIT_DIR = "$DEPOSIT_DIR
echo "N_SAMPLES = "$N_SAMPLES
echo "N_LANES = "$N_LANES
echo -e "GENOME_DIR = "$GENOME_DIR"\n"

##### Perform file organization. #####
cd $COMPUTE_HOME
cp /work/slater_lab/shared_compute_scripts/parallel_organizer.py .
source /work/slater_lab/anaconda3/bin/activate ml
python parallel_organizer.py $TARGET_DIR $DEPOSIT_DIR $N_LANES $SLURM_NTASKS
conda deactivate
rm parallel_organizer.py
chmod 700 $DEPOSIT_DIR

echo -e "File organization complete: "$(date)"\n"

##### Perform quality checks & STAR alignment for each sample. #####
cd $DEPOSIT_DIR/fastqs
mkdir quality_assessment
ls *.fastq > read_names.txt
mv read_names.txt $SLURM_HOME
cp /work/slater_lab/shared_slurm_scripts/qc_STAR_align.slurm $SLURM_HOME
cd $SLURM_HOME

while read read_name; do
    if [[ "$read_name" == *"R1"* ]]; then
    read1_name="$read_name"
    continue
    fi
    if [[ "$read_name" == *"R2"* ]]; then
    read2_name="$read_name"
    export READ1_PATH=$DEPOSIT_DIR/fastqs/"$read1_name"
    export READ2_PATH=$DEPOSIT_DIR/fastqs/"$read2_name"
    export STAR_DIR=$DEPOSIT_DIR/${read_name%_R[12].fastq}
    mkdir $STAR_DIR
    echo "Submitting "${READ1_PATH}" and "${READ2_PATH}" for alignment."
    sbatch qc_STAR_align.slurm
    unset READ1_NAME
    unset READ2_NAME
    unset STAR_DIR
    fi
done < read_names.txt

rm qc_STAR_align.slurm
rm read_names.txt

##### Format and aggregate alignment data for downstream use. #####
cp /work/slater_lab/shared_slurm_scripts/reads_aggregator.slurm $SLURM_HOME
cd $SLURM_HOME
sbatch reads_aggregator.slurm
rm reads_aggregator.slurm

##### Clean up environment. #####
unset COMPUTE_HOME
unset DEPOSIT_DIR
unset N_SAMPLES
unset GENOME_DIR

echo "Job complete: "$(date)
