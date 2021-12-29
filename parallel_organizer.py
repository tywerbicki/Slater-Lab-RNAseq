import os
import sys
import gzip
import shutil
from multiprocessing import Process

def worker_func(target, per_process_samp_dirs, deposit, n_lanes):
    """Every process spawned will run this function."""

    # Generate read tags.
    read_tags = []
    for i in range(1, 3):
        for j in range(1, n_lanes + 1):
            read_tags.append( f"L00{j}_R{i}" )

    # Enter target directory.
    os.chdir(target)

    # Iterate over each raw sample.
    for sample_dir in per_process_samp_dirs:

        if os.path.isdir( os.path.join(target, sample_dir) ):
            # Enter directory of raw sample.
            os.chdir( os.path.join(target, sample_dir) )
        else:
            # This shouldn't happen.
            print(f"Non-directory found in TARGET_DIR: {sample_dir}")
            continue

        # Order names of fastq files.
        ordered_names = [None] * len(read_tags)
        for fastq in os.listdir():
            for i, read_tag in enumerate(read_tags):
                if read_tag in fastq:
                    ordered_names[i] = fastq
                    break
        
        # Ensure all .fastq.gz files are present.
        if None in ordered_names:
            raise AttributeError(f"Couldn't locate .fastq.gz with read tag {read_tags[ ordered_names.index(None) ]} in sample {sample_dir}.")

        output_R1 = os.path.join(deposit, "fastqs", sample_dir + "_R1.fastq")
        output_R2 = os.path.join(deposit, "fastqs", sample_dir + "_R2.fastq")

        # Make file in deposit directory to store run 1.
        with open(output_R1 + ".gz", "wb") as c_out:
            message = f"Concatenated files in {sample_dir}: \n R1:"
            for i in range(n_lanes):
                with open(ordered_names[i], "rb") as c_in:
                    # Copy contents to file in deposit dir.
                    shutil.copyfileobj(c_in, c_out, length = 10485760)
                    # Record fastq.gz name.
                    message += " " + ordered_names[i]
    
        # Decompress concatenated fastqs for downstream analysis.
        with open(output_R1, "wb") as u_out:
            with gzip.open(output_R1 + ".gz", 'rb') as c_in:
                shutil.copyfileobj(c_in, u_out, length = 10485760)

        # Same as before, but now storing run 2.
        with open(output_R2 + ".gz", "wb") as c_out:
            message += "\n R2:"
            for i in range(n_lanes, n_lanes*2):
                with open(ordered_names[i], "rb") as c_in:
                    shutil.copyfileobj(c_in, c_out, length = 10485760)
                    message += " " + ordered_names[i]
    
        with open(output_R2, "wb") as u_out:
            with gzip.open(output_R2 + ".gz", 'rb') as c_in:
                shutil.copyfileobj(c_in, u_out, length = 10485760)

        # Record concatenations.     
        print(message, flush = True)
        
        # Re-enter target directory.
        os.chdir(target)

# Collect required 4 command line arguments:
# 1) Target directory.
# 2) Deposit directory.
# 3) Number of lanes in experiment.
# 4) Number of processes to spawn.
cl_args = sys.argv

if len(cl_args) != 5:
    raise AttributeError(f"4 command line arguments were expected. Got {len(cl_args) - 1}.")
if os.path.isdir(cl_args[1]):
    # Specify directory containing raw samples.
    TARGET_DIR = cl_args[1]
else:
    raise FileNotFoundError(f"Target directory '{cl_args[1]}' is not a directory.")
# Specify directory to store organized, concatenated samples.
DEPOSIT_DIR = cl_args[2]
# If deposit directory doesn't exist, make it, else return an error.
if not os.path.isdir(DEPOSIT_DIR):
    os.mkdir(DEPOSIT_DIR)
    # Make directory to deposit fastqs.
    os.mkdir( os.path.join(DEPOSIT_DIR, "fastqs") )
else:
    raise OSError(f"Deposit directory '{DEPOSIT_DIR}' already exists.")
# Specify number of lanes in experiment.
N_LANES = int( cl_args[3] )
if N_LANES < 1:
    raise ValueError("Cannot have less than 1 lane in an experiment.")
# Specify number of processes to spawn.
N_JOBS = int( cl_args[4] )
if N_JOBS < 1:
    raise ValueError("Cannot spawn less than 1 process.")

# Acquire information to be sent to each process.
sample_dir_names = os.listdir(TARGET_DIR)
n_samples = len(sample_dir_names)
n_samples_per_process = n_samples // N_JOBS
n_remaining_samples = n_samples % N_JOBS
start = 0 ; processes = []

for i in range(N_JOBS):

    if i < n_remaining_samples:
        n_process_samples = n_samples_per_process + 1
    else:
        n_process_samples = n_samples_per_process
    
    # This list contains the samples that each process will work on.
    per_process_samp_dirs = sample_dir_names[ start : (start + n_process_samples) ]
    start += n_process_samples

    p = Process(
            target = worker_func,
            args = (TARGET_DIR, per_process_samp_dirs, DEPOSIT_DIR, N_LANES)
        )
    p.start()
    processes.append(p)

for i in range(N_JOBS):
    processes[i].join()
