# Welcome To The Official Documentation For The Slater Lab RNAseq Tool.

The Slater Lab RNAseq tool is used for processing raw RNAseq data right from the sequencing machine. Its purpose is to automate many of the preprocessing steps required by an RNAseq workflow, as well as exploit their embarrassingly parallel nature to drastically decrease their cumulative execution time. Below you will find the resources necessary to become acquainted with the tool and incorporate it into your future workflows:

1. [Environment Necessities](#environment-necessities)
2. [Setting User-Defined Parameters](#setting-user-defined-parameters)
    * [COMPUTE_HOME](#compute_home)
    * [SLURM_HOME](#slurm_home)
    * [TARGET_DIR](#target_dir)
    * [DEPOSIT_DIR](#deposit_dir)
    * [N_SAMPLES](#n_samples)
    * [N_LANES](#n_lanes)
    * [GENOME_DIR](#genome_dir)
3. [Output To Expect From The Tool](#output-to-expect-from-the-tool)
4. [How To Run The Tool](#how-to-run-the-tool)
5. [Advanced Tips](#advanced-tips)

<br/>

This documentation and all source code comprising the tool are authored by *Ty Werbicki*. Please email Ty at *ty.werbicki@ucalgary.ca* with any questions, concerns, or suggestions to improve the functionality of the tool. Issue submissions are also welcome.

---

## Environment Necessities

The following is a list of necessary requirements that must be satisfied for you to be able to utilize the tool effectively:

1. A member of the *slater_lab* group on ARC. This will grant you permission to access the lab's shared workspace. This can be queried using the command: <br/>
> `groups <user>`

---

## Setting User-Defined Parameters

There are **_7_** user-defined parameters in *RNAseq.slurm* to specify:

#### COMPUTE_HOME

`COMPUTE_HOME` should specify the location to an **existing directory** wherein the tool will launch *python* scripts from. The tool will not leave any files in this directory, it is purely a location where certain processes will take place.

#### SLURM_HOME

Similar to COMPUTE_HOME, `SLURM_HOME` should specify the location to an **existing directory** wherein the tool will launch *slurm* scripts from. The tool will not leave any files in this directory, it is purely a location where certain processes will take place. It can be set to the same directory as COMPUTE_HOME if desired.

#### TARGET_DIR

`TARGET_DIR` should specify the location of the directory containing the raw sequencing data for each sample. **This must be an absolute path**.

#### DEPOSIT_DIR

`DEPOSIT_DIR` should specify the location of a directory that the tool will create and use to store all output. **This cannot be an existing directory**. **This must be an absolute path**.

#### N_SAMPLES

`N_SAMPLES` should specify the number of samples that the tool should expect to process.

#### N_LANES

`N_LANES` should specify the number of lanes used when the sequencing experiment was performed.

#### GENOME_DIR

`GENOME_DIR` should specify the location of a directory that contains the genome to be used for STAR alignment. The default value for this parameter is specifying the location to a human genome, therefore, if your experiment consists of human RNA, this parameter can be left unchanged. **This must be an absolute path**.

---

## Output To Expect From The Tool

The tool will output **a single directory** whose location and name is specified by `DEPOSIT_DIR`.

---

## How To Run The Tool

Below are step-by-step instructions on how to safely and effectively run the tool:

1. Enter directory where you normally submit slurm jobs from (this is also the directory that should be specified as `SLURM_HOME` above):
> `cd </path/to/SLURM_HOME>`
2. Copy *RNAseq.slurm* from the shared lab space into your SLURM_HOME:
> `cp /work/slater_lab/shared_slurm_scripts/RNAseq.slurm .`
3. Open *RNAseq.slurm* and change the 7 user-defined parameters to your desired values.
> `nano RNAseq.slurm` <br/>
> `Ctrl + o > Enter` to save. <br/>
> `Ctrl + x` to exit.
4. Submit *RNAseq.slurm* for batch processing.
> `sbatch RNAseq.slurm`

---

## Advanced Tips

* If you are performing a large-scale analysis (1TB+ compressed sequencing data), it is unlikely that setting `DEPOSIT_DIR` to a location in the lab's shared workspace will provide a desirable result. This is because the tool will likely run out of storage space during the data decompression step. As such, `DEPOSIT_DIR` should be set to a location in your `/scratch` directory, which provides up to 30TB of temporary storage ([see ARC storage guidelines][1]). This can be achieved by specifying:
    
    > `DEPOSIT_DIR=/scratch/${SLURM_JOB_ID}/<name_of_DEPOSIT_DIR>` 
    
    This directory will remain intact for 5 days following job completion, so you must move it back into the lab's shared workspace within that time period:
    
    > `mv /scratch/${SLURM_JOB_ID}/<name_of_DEPOSIT_DIR> /work/slater_lab/data`

---

[1]: https://rcs.ucalgary.ca/ARC_Cluster_Guide#ARC_Cluster_Storage
