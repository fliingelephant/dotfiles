---
name: use-hpc3
description: Operate the HPC3 Slurm cluster. Use for HPC3 job submission, interactive sessions, resource availability, monitoring, cancellation, storage, and environment migration, or when the project or SSH target identifies HPC3.
metadata:
  short-description: Slurm job submission and monitoring on HPC3
---

# HPC3 (Slurm) Cheat Sheet

HPC3 uses **Slurm** with GPU resources in the `acd_u`, `acd_ue`, and `emergency_acd` partitions.

Official docs: https://docs.hpc.hkust-gz.edu.cn/docs/hpc3/

## Cluster selection

Use HPC3 when the conversation, project, SSH target, job script, partition, or storage path establishes it as the target.

When multiple clusters are configured:

- Answer cluster-independent Slurm questions directly.
- For cluster-specific work, inspect the SSH configuration, existing job script, partition, paths, and requested hardware. Follow a newly specified target.
- Ask which cluster to use when the available context leaves the target unresolved. Retain the answer for subsequent work.

## Confirm parameters before execution

Before the first resource allocation for a task, **list all submission parameters and wait for explicit user approval**. This applies to `sbatch`, `srun`, and `salloc` requests for new allocations, including debug jobs, smoke tests, benchmarks, and interactive sessions.

Present the complete plan:

- Partition and account, if used.
- Selected tier, expected start time, and price for the requested allocation.
- Walltime, nodes, tasks (`-n`), CPUs per task (`-c`), and memory.
- GPU count and type; explicitly state when no GPU is requested.
- Job name, working directory, and stdout/stderr paths.
- Module loads, environment activation, relevant environment variables, and complete commands with experiment parameters.
- Additional options, including array ranges, concurrency limits, and host constraints.

Prepare the script and perform non-allocating checks before presenting the plan. Read-only inspection and script preparation can proceed directly. Include compute-based validation in the approved plan before allocating resources.

**Approval belongs to the task and parameter scope.** After a failure, inspect the logs, fix the cause, and resubmit within the approved resource and experiment settings. Report the repair and retry. Resolve an unclear failure before retrying.

Request approval again when the tier, price, resource configuration, walltime, experiment parameters, or task scope would exceed the approved plan. Steps within an approved allocation and task can proceed directly.

## Connect

Use the user's existing HPC3 SSH alias, for example `hpc3`. Inspect `ssh -G <alias>` when the target needs confirmation.

```bash
ssh hpc3
# Full hostname:
ssh <user>@hpc3login.hpc.hkust-gz.edu.cn
```

Home directory: `/data/user/<username>`.

Use the login node for editing, environment setup, and submission. Run compute workloads through Slurm.

### Scheduler and application environment

Slurm commands are available in the login environment. When checked on 2026-11-05, `sbatch`, `srun`, `sinfo`, and `scontrol` resolved under `/bin` with no modules loaded.

```bash
command -v sbatch srun sinfo scontrol
module avail
module list
```

Select the application and CUDA modules needed by the project. Include those module loads and environment activation in the job script.

## Submit a batch job

Choose the partition using the **Tier selection** policy below. Use the selected partition in the batch and interactive examples.

For one Python process, request one task and the CPUs it needs: `-N 1 -n 1 -c 8`. Configure the application's threads or workers to use the allocated CPUs. Use multiple tasks for an application that launches multiple processes.

Write `run.sh`:

```bash
#!/bin/bash
#SBATCH -J myjob
#SBATCH -p acd_u
#SBATCH -o output_%j.txt
#SBATCH -e err_%j.txt
#SBATCH -N 1
#SBATCH -n 1
#SBATCH -c 8
#SBATCH --gres=gpu:1
#SBATCH --mem=32G
#SBATCH -t 02:00:00

echo "Job started at $(date) on $(hostname)"
python your_script.py
echo "Job ended at $(date)"
```

Submit from the intended working directory:

```bash
sbatch run.sh
```

`%j` expands to the job ID in scheduler filenames. Use `--chdir=/absolute/project/path` to set a different working directory.

### GPU job

Use `--gres=gpu:N` to request GPUs per node. Each ACD node has **8 GPUs with 80 GB per GPU**. A request for 16 GPUs needs at least two nodes.

For multiple processes on one node, align the process count, CPUs per process, and GPU assignment with the application's launcher. For multiple nodes, use the platform's [distributed-job guidance](https://docs.hpc.hkust-gz.edu.cn/docs/hpc3/slurm/job/) to configure the RDMA and NCCL environment.

### Array job

```bash
#SBATCH -o output_%A_%a.txt
#SBATCH -e err_%A_%a.txt
#SBATCH --array=1-10%3
PARAM=$SLURM_ARRAY_TASK_ID
python your_script.py "$PARAM"
```

The `%3` limit allows up to three array elements to run at once. Include the total concurrent resource demand in the approval plan.

## Interactive session

```bash
srun -p acd_u -N 1 -n 1 -c 8 --mem=32G --gres=gpu:1 -t 01:00:00 --pty bash
```

The shell starts on a compute node when resources are allocated. Exit the shell to release the allocation.

## Check free CPU/GPU resources

Use these read-only queries before choosing nodes:

```bash
sinfo -o '%P %a %l %D %t %C'
sinfo -N -p acd_u,acd_ue,emergency_acd \
  -O NodeList:18,Partition:20,StateLong:18,Gres:28,GresUsed:45
scontrol show node <node>
scontrol show partition <partition>
```

- Inspect `MIXED` nodes as well as `IDLE` nodes.
- Compute free GPUs from `CfgTRES` and `AllocTRES`, or compare `Gres` with `GresUsed`. Treat an absent allocated GPU entry as zero.
- Read GPU counts directly. The `IDX` field identifies device numbers.
- Check remaining CPUs (`CPUEfctv - CPUAlloc`) and schedulable memory (`RealMemory - AllocMem`) on the same node.
- Use healthy nodes that are available for new allocations.
- Count a node once when it appears in several partitions.
- Report the partition, candidate nodes, and available resources as a current snapshot. Reservations, account limits, and priority also affect scheduling.

Use `squeue` to inspect jobs and `sinfo` / `scontrol` to inspect resources.

## Check status / monitor

```bash
squeue -u "$USER"
squeue -j <jobid>
scontrol show job <jobid>
sacct -u "$USER" --starttime=today
sacct -j <jobid> --format=JobID,State,Elapsed,MaxRSS,ReqMem,AllocCPUS,AllocTRES
tail -f output_<jobid>.txt
```

Common states: `R` = running, `PD` = pending, `CG` = completing, `F` = failed, `CD` = completed.

For a pending job, inspect the `REASON` column and `scontrol show job <jobid>`. For a finished job, inspect `sacct` and its output files.

## Cancel / extend

```bash
scancel <jobid>
scancel -u "$USER"
scontrol suspend <jobid>
scontrol resume <jobid>
```

The published runtime limit is seven days. Request an extension through an IT ticket in **Keda GO** before the job expires. The published procedure allows one extension of up to seven days. See the [queue and extension guide](https://docs.hpc.hkust-gz.edu.cn/docs/hpc3/slurm/queue/).

## Partitions and hardware (HPC3)

| Partition | Priority tier | Published user quota | Runtime limit |
|---|---|---|---|
| `acd_u` | Low | 128 CPU cores / 16 GPUs | 7d |
| `acd_ue` | Medium | 128 CPU cores / 16 GPUs | 7d |
| `emergency_acd` | High | 128 CPU cores / 16 GPUs | 7d |

Source: [partition table](https://docs.hpc.hkust-gz.edu.cn/docs/hpc3/slurm/queue/).

| Hardware | Specification | Source |
|---|---|---|
| Cluster inventory | 68 ACD nodes | official hardware table |
| GPUs per node | 8 GPUs, 80 GB each | official hardware table |
| CPU configuration | 2 sockets × 48 cores, 1 thread per core | Slurm node inspection, 2026-11-05 |
| Schedulable memory | `RealMemory=2000000` MB, approximately 2 TB | Slurm node inspection, 2026-11-05 |
| Interconnect | 400 Gb/s RoCE v2 | official platform overview |
| Storage | OceanStor; hardware table lists 16 PB | official hardware table |

The CPU and memory values describe the Slurm nodes inspected on that date. Use `scontrol show node` for a candidate node's current configuration. The published GPU specification is **80 GB ACD**; inspect the device model with `nvidia-smi` inside an approved allocation when the application needs a model-specific choice.

Sources: [hardware table](https://docs.hpc.hkust-gz.edu.cn/docs/intro/hardware/) and [platform overview](https://docs.hpc.hkust-gz.edu.cn/docs/intro/).

### Tier selection

**Choose the earliest expected start time, then the lowest price among equally fast options.** Consider all available tiers that fit the requested hardware, memory, walltime, account access, and stated budget.

Compare `acd_u`, `acd_ue`, and `emergency_acd` using live resource and queue data. Check the same resource request in each compatible partition with `sbatch --test-only -p <partition> run.sh`; this validates the request and provides a start-time estimate without submitting a job. See the [Slurm command reference](https://slurm.schedmd.com/sbatch.html#OPT_test-only).

Compare the price of the full requested allocation using the [current pricing table](https://docs.hpc.hkust-gz.edu.cn/docs/charges/prices-phaseIII/). Present the selected partition, tier, expected start, and price with the resource parameters for approval.

Use the selected partition's configured priority. Check the current partition and account limits, and set CPU count, memory, GPU count, and walltime explicitly.

## Storage

The shared user filesystem is mounted at `/data`. Home directories are `/data/user/<username>`.

### Where to put what

Use a project layout under the home directory:

| Content | Suggested path |
|---|---|
| Code and configuration | `~/projects/<project>` |
| Conda environments | `~/envs/<environment>` |
| Datasets | `~/data/<dataset>` |
| Checkpoints and experiment output | `~/runs/<experiment>` |

Inspect the destination filesystem and available space before transferring large datasets:

```bash
findmnt -T "$HOME"
df -h "$HOME"
du -sh /path/to/project
```

The portal's **Data Management** view exposes the home directory. See the [file-management guide](https://docs.hpc.hkust-gz.edu.cn/docs/hpc3/data/data-manage/).

### Quotas

Use the portal to check account storage limits. Use `df` to inspect filesystem capacity and `du` to inspect a project's usage.

## Packages and environment migration

HPC3 restricts Internet access. Install packages through the internal mirror, or prepare an environment on HPC2 and transfer it. See the [mirror guide](https://docs.hpc.hkust-gz.edu.cn/docs/hpc3/on-campus-repository/) and [migration guide](https://docs.hpc.hkust-gz.edu.cn/docs/hpc3/hpc2-migrate/).

### Install from the internal Python mirror

Run inside the intended environment on HPC3:

```bash
getent hosts harbor.internal.com
python -m pip install <package> \
  --index-url http://harbor.internal.com:8081/repository/pypi-hkust/simple \
  --trusted-host harbor.internal.com
```

For Conda and other package types, use the repository URLs in the mirror guide. Keep environment-specific package settings with the project.

### Move a Conda environment from HPC2

On HPC2, install `conda-pack` in the packing environment and pack the selected environment:

```bash
conda install -c conda-forge conda-pack
conda pack -n myenv -o myenv.tar.gz
```

On HPC3, copy and unpack it:

```bash
scp <user>@hpc2login.hpc.hkust-gz.edu.cn:/absolute/path/myenv.tar.gz ~/
mkdir -p ~/envs/myenv
tar -xzf ~/myenv.tar.gz -C ~/envs/myenv
source ~/envs/myenv/bin/activate
conda-unpack
```

Include the environment activation in the HPC3 job script. Run the application's first compute test within the approved allocation plan.

## Baseline principle: validate before sbatch

Before allocating compute resources:

1. Check the script with `bash -n run.sh`.
2. Confirm the interpreter, environment, inputs, working directory, and log directories.
3. Check the requested resources against compatible partitions and candidate nodes.
4. Use `sbatch --test-only run.sh` to check the scheduler request without allocating resources.
5. Include a short test in the approved plan, using the tier-selection policy to choose its partition. Check the environment, GPU visibility, and one representative unit of work.
6. Use the test's runtime and memory use to size the production job.

Compute-based tests follow the allocation approval rule above.

## Walltime: how to pick `-t`

Set a limit of about **1.5–2× the measured runtime**. For a new workload, time one representative unit in an approved short job, then scale by the number of units. Save checkpoints during long runs.

After completion, use `sacct` to compare elapsed time with the requested limit and refine the next request.

Formats: `-t 30` for 30 minutes, `-t 02:00:00` for two hours, and `-t 1-12:00:00` for one day and twelve hours.

## Common gotchas

- **Partition selection:** use HPC3 partition names such as `acd_u`.
- **Task count:** `-n` sets tasks and `-c` sets CPUs per task. A single-process job typically uses `-n 1`.
- **GPU count:** `--gres=gpu:N` requests N GPUs on each allocated node.
- **Memory:** set `--mem` explicitly for a per-node memory request.
- **Packages:** use the internal mirror or a transferred environment.
- **Environment setup:** include module loads and activation commands in the job script.
- **Distributed jobs:** use the current platform RDMA/NCCL settings for the selected nodes and software stack.
- **Log paths:** create output directories before submitting.
- **Completed jobs:** inspect `sacct` and the logs after a job leaves `squeue`.

## Related workflows

- Use the HPC1 skill for UniScheduler jobs and the HPC2 skill for HPC2 partitions and storage.
- Use the [container quick start](https://docs.hpc.hkust-gz.edu.cn/docs/hpc3/k8s/quick-start/) for portal-managed development environments and container jobs.
