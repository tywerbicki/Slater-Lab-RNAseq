import sys
import os
from time import sleep
import pandas as pd
import pyarrow.feather as feather

# Collect required 2 command line arguments:
# 1) Deposit directory.
# 2) Number of expected samples.
cl_args = sys.argv

if len(cl_args) != 3:
    raise AttributeError(f"2 command line arguments were expected. Got {len(cl_args) - 1}.")
if os.path.isdir(cl_args[1]):
    # Specify directory containing alignment directories.
    DEPOSIT_DIR = cl_args[1]
else:
    raise FileNotFoundError(f"Deposit directory '{cl_args[1]}' is not a directory.")
# Specify number of samples to expect.
N_SAMPLES = int( cl_args[2] )
if N_SAMPLES < 1:
    raise ValueError("Cannot expect less than 1 sample.")

# Enter deposit directory.
os.chdir(DEPOSIT_DIR)

# Wait until all reads data has arrived.
check_num = 0
n_reads_data = 0
while n_reads_data < N_SAMPLES:

    # Wait 5 minutes.
    sleep(60 * 5)
    n_reads_data = 0
    
    for sample_dir in os.listdir():
        
        if os.path.isdir( os.path.join(DEPOSIT_DIR, sample_dir) ):
            # Enter sample's alignment directory.
            os.chdir( os.path.join(DEPOSIT_DIR, sample_dir) )
        else:
            # This shouldn't happen.
            print(f"Non-directory found in DEPOSIT_DIR: {sample_dir}")
            continue
        # Check for presence of flag indicating completion of alignment.
        if "DONE.txt" in os.listdir():
            n_reads_data += 1
        # Return to deposit directory.
        os.chdir("..")
    
    check_num += 1
    print(f"Check {check_num}: {n_reads_data} out of {N_SAMPLES} samples have been aligned.", flush = True)

aggregated_data = None

for sample_dir in os.listdir():

    if os.path.isdir( os.path.join(DEPOSIT_DIR, sample_dir) ):
        # Enter sample's alignment directory.
        os.chdir( os.path.join(DEPOSIT_DIR, sample_dir) )
    else:
        # This shouldn't happen.
        continue

    # Confirm presence of reads file.
    if "ReadsPerGene.out.tab" not in os.listdir():
        continue
    # Remove flag.
    os.remove("DONE.txt")
        
    if aggregated_data is None:

        aggregated_data = (
            pd.read_csv(
                filepath_or_buffer = "ReadsPerGene.out.tab",
                sep = "\t",
                header = None,
                usecols = [0, 1],
                skiprows = 4
            )
            .rename(columns = {0:"ID", 1:sample_dir})
            .astype({sample_dir:"int32"})
            .set_index("ID")
        )

    else:

        temp_data = (
            pd.read_csv(
                filepath_or_buffer = "ReadsPerGene.out.tab",
                sep = "\t",
                header = None,
                usecols = [0, 1],
                skiprows = 4
            )
            .rename(columns = {0:"ID", 1:sample_dir})
            .astype({sample_dir:"int32"})
            .set_index("ID")
        )

        # Append reads data by index with sample directory as column name.
        aggregated_data = aggregated_data.join(
            other = temp_data,
            how = "inner"
        )
    
    # Return to deposit directory.
    os.chdir("..")

# Sanity check.
print(aggregated_data.head(10), flush = True)

# Write aggregated data to feather format for DE analysis.
# Have to reset index because feather doesn't support row names.
feather.write_feather(
    df = aggregated_data.reset_index(),
    dest = "read_data_agg",
    compression = "lz4",
    version = 2
)