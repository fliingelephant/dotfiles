---
name: use-hpc1
description: Operate the HPC1 UniScheduler cluster. Use for HPC1 job submission, interactive sessions, resource availability, monitoring, cancellation, and storage, or when the project or SSH target identifies HPC1.
metadata:
  short-description: UniScheduler job submission and monitoring on HPC1
---

# HPC1 (UniScheduler) Cheat Sheet

HPC1 uses **JH UniScheduler**, with `jsub` commands and LSF-style `#BSUB` directives.

Official docs: https://docs.hpc.hkust-gz.edu.cn/docs/hpc12/slurm/job1/

## Cluster selection

Use HPC1 when the conversation, project, SSH target, job script, queue, or storage path establishes it as the target.

When multiple clusters are configured:

- Answer general scheduler questions directly.
- For cluster-specific work, inspect the SSH configuration, existing job script, queue, paths, and requested hardware. Follow a newly specified target.
- Ask which cluster to use when the available context leaves the target unresolved. Retain the answer for subsequent work.

## Confirm parameters before execution

Before the first resource allocation for a task, **list all submission parameters and wait for explicit user approval**. This includes batch jobs, interactive sessions, debug runs, smoke tests, and benchmarks submitted through `jsub`.

Present the complete plan:

- Queue and project, if used.
- Selected tier, expected start time, and price for the requested allocation.
- Walltime (`-W`), host count (`-hosts`), CPU count (`-n`), and memory limit (`-M`, in MB).
- GPU count and type; explicitly state when no GPU is requested.
- Job name, working directory, and stdout/stderr paths.
- Module loads, environment activation, relevant environment variables, and complete commands with experiment parameters.
- Additional options, including array ranges, host constraints, and resource expressions.

Prepare the script and perform non-allocating checks before presenting the plan. Read-only inspection and script preparation can proceed directly. Include compute-based validation in the approved plan before allocating resources.

**Approval belongs to the task and parameter scope.** After a failure, inspect the logs, fix the cause, and resubmit within the approved resource and experiment settings. Report the repair and retry. Resolve an unclear failure before retrying.

Request approval again when the tier, price, resource configuration, walltime, experiment parameters, or task scope would exceed the approved plan. Steps within an approved allocation and task can proceed directly.

## Connect

Use the user's existing HPC1 SSH alias, for example `hpc1`. Inspect `ssh -G <alias>` when the target needs confirmation.

```bash
ssh hpc1
# Full hostname:
ssh <user>@hpc1login.hpc.hkust-gz.edu.cn
```

Home directory: `/hpc/home/<username>`.

Use the login node for editing, environment setup, and submission. Run compute workloads through `jsub`.

### Load the scheduler environment with a login shell

HPC1's login startup configures UniScheduler. For commands sent over SSH, start a login shell:

```bash
ssh hpc1 'bash -lc "jqueues"'
```

In the login shell:

```bash
command -v jsub jqueues jhosts jjobs
module avail
```

The scheduler commands were available under `/opt/jhinno64/unischeduler/linux-x86_64/bin` when checked on 2026-11-05. Include the application's module loads and environment activation in its job script.

## Submit a batch job

Choose the queue using the **Tier selection** policy below. Use the selected queue in the batch and interactive examples.

For one process with eight CPU cores, request `-n 8 -hosts 1`. Configure the application's thread count to use those cores.

Write `run.sh`:

```bash
#!/bin/bash
#BSUB -J myjob
#BSUB -q normal
#BSUB -o output_%J.txt
#BSUB -e err_%J.txt
#BSUB -n 8
#BSUB -hosts 1
#BSUB -M 16384
#BSUB -W 02:00

echo "Job started at $(date) on $(hostname)"
python your_script.py
echo "Job ended at $(date)"
```

Submit from the intended working directory:

```bash
jsub < run.sh
```

`%J` expands to the job ID in scheduler filenames. The job uses the submission directory by default; use `-cwd /absolute/project/path` to set another directory.

### GPU job

Use the `gpu` queue and request GPUs with `-gpgpu`:

```bash
#BSUB -q gpu
#BSUB -gpgpu 1
#BSUB -n 8
#BSUB -hosts 1
#BSUB -M 32768
#BSUB -W 04:00
```

Each GPU node has **8 NVIDIA A30 GPUs with 24 GB per GPU**. Use `jhosts -l <node>` to inspect the available devices and their scheduler type names.

### Array job

Add an array range and a separate output file for each element:

```bash
#BSUB -J sweep[1-10]
#BSUB -o output_%J_%I.txt
#BSUB -e err_%J_%I.txt
```

`%I` expands to the array index in scheduler filenames. Quote the array name when passing it through a shell, for example `-J 'sweep[1-10]'`.

## Interactive session

```bash
jsub -I -q normal -n 4 -hosts 1 -M 8192 -W 01:00 bash
jsub -I -q gpu -gpgpu 1 -n 8 -hosts 1 -M 32768 -W 01:00 bash
```

The shell starts on a compute node when the job is dispatched. Exit the shell to release the allocation.

## Check free CPU/GPU resources

Run these read-only queries from the login shell:

```bash
jqueues
jqueues -l normal gpu lmem
jhosts -w
jhosts -l <node>
jhosts stat -l <node>
```

- Select an `Open:Active` queue and inspect its host group and current limits.
- Use the host's CPU slot counts, reservations, memory, and state to assess whether the request fits.
- For GPUs, read the per-device table in `jhosts -l`. Count available full GPUs and report MIG instances separately.
- Check CPU, memory, and GPU capacity on the same candidate host.
- Report the queue, candidate hosts, and available resources as a current snapshot. Account limits and scheduling priority also affect dispatch.

Use `jjobs` to inspect jobs and `jqueues` / `jhosts` to inspect resources.

## Check status / monitor

```bash
jjobs -u "$USER"
jjobs -l <jobid>
jjobs -p
jjobs -A
jhist -u "$USER"
tail -f output_<jobid>.txt
```

Common states: `PEND` = waiting, `RUN` = running, `PSUSP` / `USUSP` / `SSUSP` = suspended, `DONE` = finished, `EXIT` = exited with an error or termination.

For a waiting job, inspect `jjobs -l <jobid>` and `jjobs -p`. For a finished job, inspect its history and output files.

## Cancel / extend

```bash
jctrl kill <jobid>
jctrl stop <jobid>
jctrl resume <jobid>
```

Extend a job through the platform portal: **My Jobs → select the HPC1 job → Extend Time**. The published procedure allows one extension of up to seven days. See the [job extension guide](https://docs.hpc.hkust-gz.edu.cn/docs/hpc12/slurm/queue/).

## Queues and hardware (HPC1)

| Queue | Nodes | Hardware per node | Published default runtime | Use for |
|---|---:|---|---|---|
| `normal` | 10 | 56 CPU cores / 256 GB | 7d | shared CPU |
| `gpu` | 4 | 56 CPU cores / 384 GB / 8 A30 GPUs, 24 GB each | 7d | shared GPU |
| `lmem` | 2 | 96 CPU cores / 1.5 TB | 7d | large memory |

The CPU and GPU nodes use two Intel Xeon Gold 6348 CPUs. The large-memory nodes have four 24-core CPUs. The cluster has 100 Gb/s InfiniBand and 701 TB of shared storage. Sources: [hardware table](https://docs.hpc.hkust-gz.edu.cn/docs/intro/hardware/), [platform overview](https://docs.hpc.hkust-gz.edu.cn/docs/intro/), and [queue table](https://docs.hpc.hkust-gz.edu.cn/docs/hpc12/slurm/queue/).

Set walltime explicitly. Read the current queue limits with `jqueues -l <queue>` when preparing a submission.

### Tier selection

**Choose the earliest expected start time, then the lowest price among equally fast options.** Consider all available tiers that fit the requested hardware, memory, walltime, account access, and stated budget.

Use `jqueues` and `jhosts` to compare queue demand, available hosts, resource reservations, and scheduling priority. Explain the basis of the expected start time in the submission plan.

| Tier | Queue priority | Published queues |
|---|---:|---|
| Low | 10 | `normal`, `gpu`, `lmem` |

The priority values were checked on 2026-11-05. Inspect `jqueues -l` for current tiers and access. Use the selected queue's configured priority.

Compare the price of the full requested allocation using the [current pricing table](https://docs.hpc.hkust-gz.edu.cn/docs/charges/prices-phaseI&II/). Present the selected queue, tier, expected start, and price with the resource parameters for approval.

## Storage

HPC1 uses a shared BeeGFS filesystem mounted at `/hpc`.

| Path | Use |
|---|---|
| `/hpc/home/<user>` | home directory, code, environments, and results |
| `~/jhspoolers` | portal job-data area at `/hpc/jhinno62/JH_DATA/spooler/<user>` |
| `~/jhupload` | portal upload area inside the spooler directory |

These paths and symlinks were checked on 2026-11-05. Home and portal job data both reside on `/hpc`.

### Where to put what

- Keep code and environments in the home directory.
- Put each experiment's outputs and checkpoints in its own project directory.
- Use `~/jhspoolers` for files managed through the portal job-data interface.
- Check the destination filesystem and available space before copying large datasets.

```bash
findmnt -T "$HOME"
readlink -f ~/jhspoolers
df -h "$HOME"
du -sh /path/to/project
```

### Quotas

Use the portal to check the account's storage quota. Use `df` to inspect filesystem capacity and `du` to inspect a project's usage.

## Baseline principle: validate before jsub

Before allocating compute resources:

1. Check the script with `bash -n run.sh`.
2. Confirm the interpreter, environment, input paths, working directory, and log directories.
3. Check the queue and requested resources with `jqueues` and `jhosts`.
4. Include a short test in the approved plan. Choose its queue using the tier-selection policy and the test's resource requirements.
5. Use the test's runtime and memory use to size the production job.

Use `jsub -h` to check the installed client's submission options. Compute-based tests follow the allocation approval rule above.

## Walltime: how to pick `-W`

Set a limit of about **1.5–2× the measured runtime**. Use `HH:MM`, for example `-W 02:00` for two hours.

For a new workload, time one representative unit in an approved short job, then scale by the number of units. Save checkpoints during long runs. Use job history and logs to refine the next request.

## Common gotchas

- **Scheduler command missing:** run remote commands through a login shell, such as `ssh hpc1 'bash -lc "jqueues"'`.
- **Submission syntax:** use `#BSUB` directives and submit with `jsub < run.sh`.
- **Memory units:** the installed client's `-M` value is in MB.
- **CPU allocation:** set both `-n` and the application's thread/process configuration. Use `-hosts 1` for a job that runs on one host.
- **GPU allocation:** choose `gpu` and include `-gpgpu N`.
- **Array names:** quote bracketed ranges in shell commands.
- **Environment setup:** include the required module loads and activation commands in the job script.
- **Log paths:** create output directories before submitting.

## Related workflows

- Use the HPC2 or HPC3 skill for their Slurm workflows.
- Use the [container guide](https://docs.hpc.hkust-gz.edu.cn/docs/hpc12/k8s/feature-preview/) for portal-managed AI development environments.
