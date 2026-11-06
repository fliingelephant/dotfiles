---
name: use-hpc2
description: Operate the HPC2 Slurm cluster. Use for HPC2 job submission, interactive sessions, resource availability, monitoring, cancellation, and storage, or when the project or SSH target identifies HPC2.
metadata:
  short-description: Slurm job submission and monitoring on HPC2
---

# HPC2 (Slurm) Cheat Sheet

HPC2 uses **Slurm**. HPC1 uses LSF (`jsub` / `#BSUB`), while HPC4 has different Slurm partitions and a separate AIStudio NPU workflow. Do not mix them.

Official docs: https://docs.hpc.hkust-gz.edu.cn/docs/hpc12/

## Cluster selection

This skill targets HPC2. Keep using HPC2 when it is established by the conversation, project, SSH target, job script, partition, or storage path. Do not ask about other clusters when the target is clear.

When multiple cluster targets are configured:

- Answer cluster-independent Slurm questions without choosing a cluster.
- For cluster-specific work, inspect available read-only context first: current hostname, SSH target/config, existing job script, partition, paths, and requested hardware. A new explicit target replaces older context.
- Ask which cluster the user uses only when a cluster-specific action or command still cannot be chosen safely, or when the evidence conflicts. Once answered, retain it for the rest of the conversation.

## Confirm parameters before execution

Before the first resource allocation for a task, **list all submission parameters and wait for explicit user approval**. A generic request to train, run, or optimize is not approval of submission parameters. This applies to `sbatch`, `srun` or `salloc` requesting a new allocation, including debug jobs, smoke tests, benchmarks, and interactive sessions. Steps within an already approved allocation and task need no additional approval.

Present the complete plan with no silent resource defaults:

- Partition and account if used.
- Selected tier, expected start time, and price for the requested allocation.
- Walltime, nodes, tasks (`-n`), CPUs per task (`-c`), and memory.
- GPU count and type; explicitly state when no GPU is requested.
- Job name, working directory, and stdout/stderr paths.
- Module loads, environment activation, relevant environment variables, and complete commands with experiment parameters.
- All additional scheduler options, including array ranges and concurrency limits when used.

Prepare the script and perform non-allocating checks before presenting the final plan. Read-only inspection and script preparation need no submission approval. Include compute-based validation in the approved plan or confirm it separately before allocating resources.

**Approval belongs to the confirmed task and parameter scope, not to one submission attempt.** When the same task fails, diagnose and repair code, environment, or path errors and resubmit within the approved resource and experiment settings without asking again. Report the repair and retry. If the cause is unclear or the same error persists, diagnose before another attempt; do not blindly loop submissions.

Ask for confirmation again only when tier, price, resource configuration, walltime, experiment parameters, or task scope would exceed the confirmed plan. Present the concrete changes before proceeding. Explicitly approved groups of submissions or parameter ranges remain authorized within their bounds. Failure recovery does not authorize additional experiments or unapproved optimization changes.

## Connect

Use the user's existing HPC2 SSH alias (for example, `hpc2`). Inspect `ssh -G <alias>` if the target is unclear; the skill name does not create an SSH alias.

```bash
ssh hpc2                 # example: an existing HPC2 alias
# or
ssh <user>@hpc2login.hpc.hkust-gz.edu.cn
```

Home directory: `/hpc2hdd/home/<username>`

Login node is for editing/compiling/submitting only — never run heavy compute there. Use `srun` for interactive work.

### Load Slurm before any sbatch/srun/squeue

The login node's `/usr/bin/sbatch` etc. exist but are misconfigured (`slurm.conf` not at default path). You **must** load the Slurm module first or every Slurm command fails with `Unable to process configuration file`:

```bash
module load slurm
which sinfo   # → /opt/slurm/bin/sinfo  (correct one)
```

Make it permanent by appending to `~/.bashrc`:
```bash
echo 'module load slurm' >> ~/.bashrc
```

Compute nodes inside a job don't need this — they have a working local Slurm. The module is only for the login node where you submit/monitor from.

## Submit a batch job

Choose the partition using the **Tier selection** policy below. Use the selected partition in the batch and interactive examples.

For one Python process, request one task and the CPUs it needs: `-N 1 -n 1 -c 8`. `-n` counts tasks/processes; `-c` allocates CPUs per task and does not itself create application threads. Use multiple tasks only for an intended multi-process workload.

Write a script, e.g. `run.sh`:

```bash
#!/bin/bash
#SBATCH -J myjob              # job name
#SBATCH -p i64m512u           # partition (see table below)
#SBATCH -o output_%j.txt      # stdout, %j = jobid
#SBATCH -e err_%j.txt         # stderr
#SBATCH -N 1                  # one node
#SBATCH -n 1                  # one process
#SBATCH -c 8                  # eight CPUs for that process
#SBATCH --mem=16G             # memory
#SBATCH -t 02:00:00           # walltime HH:MM:SS

echo "Job started at $(date) on $(hostname)"
python your_script.py
echo "Job ended at $(date)"
```

Submit:
```bash
sbatch run.sh                 # → "Submitted batch job <jobid>"
```

### GPU job

```bash
#SBATCH -p i64m1tga800u       # A800 partition
#SBATCH --gres=gpu:1          # 1 GPU; use gpu:2 etc.
#SBATCH -N 1                  # one node
#SBATCH -n 1                  # one process using the GPU
#SBATCH -c 8                  # eight CPUs for that process
#SBATCH --mem=32G
#SBATCH -t 04:00:00
```

A800 and A40 nodes each have **8 GPUs per node**. The published 16-GPU shared-partition resource limit is not a per-node hardware specification; allocating 16 GPUs requires at least two such nodes.

### Array job

```bash
#SBATCH -o output_%A_%a.txt   # %A=array id, %a=task id
#SBATCH --array=1-10          # or 1-10%3 to cap concurrency at 3
PARAM=$SLURM_ARRAY_TASK_ID
python your_script.py $PARAM
```

## Interactive session

```bash
srun -p i64m512u -N 1 -n 1 -c 4 --mem=8G -t 01:00:00 --pty bash
srun -p i64m1tga800u -N 1 -n 1 -c 8 --mem=32G --gres=gpu:1 -t 01:00:00 --pty bash
```

Land in a shell on a compute node. Exit with `exit` to release the allocation.

## Check free CPU/GPU resources

After `module load slurm`, use these read-only queries to compare compatible partitions across tiers:

```bash
# Partition state and CPU counts: allocated / idle / other / total
sinfo -o '%P %a %l %D %t %C'

# Node inventory and allocation; supply comma-separated candidate partitions
sinfo -N -p <candidate-partitions> \
  -O NodeList:18,Partition:20,StateLong:18,Gres:28,GresUsed:45

# Inspect a candidate node and the chosen partition
scontrol show node <node>
scontrol show partition <partition>
```

- A partition being `UP` means it accepts jobs, not that resources are free. `MIXED` nodes can have spare resources; do not search only for `IDLE` nodes.
- For GPUs, compare `Gres` with `GresUsed`, or subtract `AllocTRES`'s `gres/gpu` from `CfgTRES`'s `gres/gpu`. An absent GPU allocation entry means zero allocated GPUs. Do not add the typed GPU count (such as `gres/gpu:a40`) to the total: they describe the same devices.
- Read the GPU **count**, not the `IDX` device numbers. For example, `gpu:a40:8` configured and `gpu:a40:7(IDX:0-4,6-7)` allocated leaves one unallocated GPU.
- Exclude down, draining, failed, maintenance, and unresponsive nodes. Planned/reserved capacity needs separate consideration. Check remaining CPUs (`CPUEfctv - CPUAlloc`) and schedulable memory (`RealMemory - AllocMem`) on the **same node**; `FreeMem` is an operating-system reading, not the scheduler's allocation balance.
- Report the partition, candidate nodes, and unallocated resources as a current snapshot. Reservations, account/QOS limits, priority, and other jobs can prevent an immediate start. Nodes can belong to multiple partitions; do not double-count them across partitions.

`squeue` answers which jobs are running or waiting; `sinfo` and `scontrol` answer which resources are configured and allocated. Do not submit a job merely to inspect availability.

## Check status / monitor

```bash
squeue -u $USER                       # my running + pending jobs
squeue -j <jobid>                     # one job
scontrol show job <jobid>             # full details: paths, resources, why pending
sacct -u $USER --starttime=today      # today's history
sacct -j <jobid> --format=JobID,State,Elapsed,MaxRSS,ReqMem,AllocCPUS,AllocGRES
                                      # post-mortem: how much was actually used
tail -f output_<jobid>.txt            # live stdout from login node
ssh <nodename> top                    # `scontrol show job` shows NodeList; peek with top
```

State codes from `squeue`: `R`=running, `PD`=pending, `CG`=completing, `F`=failed, `CD`=completed.

If a job is stuck in `PD`, the `REASON` column tells you why (`Resources`, `Priority`, `QOSMaxJobsPerUserLimit`, etc.).

## Cancel / extend

```bash
scancel <jobid>                       # cancel one
scancel -u $USER                      # cancel all mine
scontrol suspend <jobid>              # pause (rarely needed)
scontrol resume <jobid>
```

Extending walltime is **not** a CLI op here — go to the platform portal → "My Jobs" → "Extend Time". Max +7 days per request, hard ceiling 14 days. For longer, file a ticket.

## Partitions (HPC2)

| Partition | Hardware per node | Published resource limit | Wall limit | Use for |
|---|---|---|---|---|
| `i64m512u` | 64 CPU cores / 512 GB | 1024 CPU cores | 7d | shared CPU |
| `i64m512ue` | 64 CPU cores / 512 GB | 1024 CPU cores | 7d | exclusive CPU |
| `long_cpu` | 64 CPU cores / 512 GB | 1024 CPU cores | 14d | long CPU runs |
| `emergency_cpu` | 64 CPU cores / 512 GB | 512 CPU cores | check live | premium CPU |
| `a128m512u` | 128 AMD cores / 512 GB | 256 CPU cores | 7d | shared AMD CPU |
| `i64m1tga800u` | 64 CPU cores / 8 A800 / 1024 GB | 128 CPU cores / 16 GPUs | 7d | shared A800 |
| `i64m1tga800ue` | 64 CPU cores / 8 A800 / 1024 GB | 64 CPU cores / 8 GPUs | 7d | exclusive A800 |
| `long_gpu` | 64 CPU cores / 8 A800 / 1024 GB | 128 CPU cores / 16 GPUs | 14d | long GPU runs |
| `i64m1tga40u` | 64 CPU cores / 8 A40 / 1024 GB | 128 CPU cores / 16 GPUs | 7d | shared A40 |
| `i64m1tga40ue` | 64 CPU cores / 8 A40 / 1024 GB | 64 CPU cores / 8 GPUs | 7d | exclusive A40 |
| `i96m3tu`, `i96m3tue` | 96 CPU cores / 3 TB | 192 CPU cores | 7d | large memory |
| `debug` | mixed CPU nodes and an 8-A40 GPU node | 16 CPU cores / 2 GPUs | **0.5h** | **free** debugging |

The resource-limit column follows the [official cluster table](https://docs.hpc.hkust-gz.edu.cn/docs/hpc12/slurm/queue/). These are policy limits, not hardware counts or current availability. Check live node/partition data and account limits before sizing a job.

`u` = shared (lower priority, lower rate), `ue` = exclusive node (higher).

### Tier selection

**Choose the earliest expected start time, then the lowest price among equally fast options.** Consider all available tiers that fit the requested hardware, memory, walltime, account access, and stated budget.

| Priority tier | Partitions |
|---|---|
| Low (100) | `*u`, `long_*`, `i64m512r` |
| Medium (200) | `*ue`, `i64m512re` |
| High (300) | `emergency_cpu`, `emergency_gpu`, `emergency_gpua40` |

Use live `sinfo` and `scontrol` data to identify compatible candidates. Compare the same resource request across candidates with `sbatch --test-only -p <partition> run.sh`; this validates the request and provides a start-time estimate without submitting a job. See the [Slurm command reference](https://slurm.schedmd.com/sbatch.html#OPT_test-only).

Include `debug` when a short test fits its hardware and runtime limits. Apply the same start-time and price rule to that test.

Compare the price of the full requested allocation using the [current pricing table](https://docs.hpc.hkust-gz.edu.cn/docs/charges/prices-phaseI&II/). Present the selected partition, tier, expected start, and price with the resource parameters for approval.

Use the selected partition's configured priority. Leave `--qos` and `--priority` at the cluster defaults.

## Storage

Two GPFS pools:

| Mount | Type | Size | Use |
|---|---|---:|---|
| `/hpc2hdd` | HDD | 3.9 PB (often >90% full) | bulk, long-term, slower |
| `/hpc2ssd` | SSD | smaller | fast scratch I/O |

Home is `/hpc2hdd/home/<user>`. Inside it, several **symlinks** map portal-managed areas — pay attention to which point at SSD vs HDD:

| Symlink | Target | What it really is |
|---|---|---|
| `~/jhspoolers` | `/hpc2ssd/JH_DATA/spooler/<user>` | **SSD scratch** — the only fast-I/O area you get |
| `~/jhupload` | `/hpc2ssd/JH_DATA/spooler/<user>/.upload` | portal upload landing on SSD |
| `~/jhaidata` | `/hpc2hdd/JH_DATA/jhai_data/<user>` | AI data area (HDD), large datasets |
| `~/.jhshares` | `/hpc2hdd/JH_DATA/share/<user>` | shared with your group |
| `~/.filedownload` | `/hpc2hdd/JH_DATA/filedownload/<user>` | portal download staging |

### Where to put what

| Content | Path | Why |
|---|---|---|
| Code, configs, scripts, conda env | `~/` (home, HDD) | small, persistent |
| Read-only datasets (long-term) | `~/jhaidata` | big, HDD is fine |
| Training intermediates, checkpoints, unpacked dataset cache | **`~/jhspoolers` (SSD)** | hot-path I/O |
| Group-shared data | `~/.jhshares` | visible to your group |

### Using SSD scratch in a job

```bash
mkdir -p ~/jhspoolers/job-$SLURM_JOB_ID
cd ~/jhspoolers/job-$SLURM_JOB_ID
cp ~/jhaidata/big_dataset.tar.gz . && tar xf big_dataset.tar.gz
python ~/code/train.py --data ./extracted --ckpt-dir ./ckpts
# afterwards: archive final results back to HDD, then clean up SSD
cp ckpts/final.pt ~/results/
```

Rule of thumb: heavy random/repeat-read I/O on SSD, archival on HDD.

### Quotas

`quota` / `lfs quota` / `mmlsquota` are **not installed** on the login node — quota is only visible via the portal. Each pool (HDD/SSD) and each portal-managed area is counted separately. If a write fails with `Disk quota exceeded`, check the portal, not the filesystem.

## Baseline principle: validate before sbatch

Compute time is billed once the job starts. Burning a 4-hour GPU slot on a typo is avoidable. Before `sbatch`:

1. **Dry-run the script logic locally or in `srun --pty`** with tiny inputs.
2. **Choose a short smoke test using the tier-selection policy.** Include `debug` among candidates when the test fits its resources and 30-minute limit. Use the selected partition to confirm modules load, paths resolve, and the GPU is visible (`nvidia-smi`).
3. **Right-size walltime and resources.** Easier to extend (portal) or rerun than to overpay. After the first real run, use `sacct -j <jobid> --format=...MaxRSS,Elapsed` to calibrate future jobs.
4. **Sanity-check the submit script:** `bash -n run.sh` (syntax), confirm output/error dirs exist, confirm `--gres=gpu:N` only on GPU partitions. Then use `sbatch --test-only run.sh` to validate the resource request without submitting or allocating a job; any reported start time is an estimate, not a reservation.

These validation steps follow the confirmation rule above: include their resource requests and commands in the approved plan before running them.

## Walltime: how to pick `-t`

It's an **upper bound**, not a fixed duration — script exits early, resources release immediately. Two forces pull opposite ways:

- **Too low** → `TIMEOUT` kills the job mid-run.
- **Too high** → lower scheduling priority, longer pending.

Billing is on actual elapsed time, not requested walltime, so overestimating doesn't cost more — just slower to start. Aim for **~1.5–2× your real estimate**.

First-time estimation:

1. **Time the smallest unit in an approved short job** — 1 epoch / 1 iter / small slice. Choose its partition using the tier-selection policy. Example for a selected `debug` allocation:
   ```bash
   srun -p debug -N 1 -n 1 -c 8 --mem=8G --gres=gpu:1 -t 00:30:00 time python train.py --epochs 1
   ```
   Then `total ≈ unit_time × units × 1.5`.
2. **Calibrate from local**: A800 ≈ 1.5–2× a 4090; A40 ≈ 0.5–0.8× a 4090; HPC2 CPU ≈ 5–20× a laptop (per-core × core count).
3. **Always checkpoint** in long jobs (`torch.save` per epoch, etc.) — a TIMEOUT only costs the unsaved tail.
4. **After the first real run**, `sacct -j <jobid> --format=JobID,Elapsed,Timelimit` shows actual vs requested → tighten next time.

Format: `-t 30` (30 min) · `-t 02:00:00` (HH:MM:SS) · `-t 1-12:00:00` (D-HH:MM:SS). Use a dash, not space, between days and time.

## Common gotchas

- **Wrong partition for GPU**: `--gres=gpu:1` on a CPU partition → job fails or pends forever. Match partition to resource.
- **`-n` vs `-c`**: `-n` = number of tasks (processes/MPI ranks), `-c`/`--cpus-per-task` = CPUs allocated per task. For a single multi-threaded process use `-n 1 -c 8` and configure the application's thread count; `srun -n 8 python ...` launches eight Python processes.
- **Output file path not writable**: `-o`/`-e` paths are evaluated at submission time. Relative paths resolve against the submission directory unless `-D` overrides.
- **Modules not loaded inside the script**: login shell ≠ batch shell. `module load …` (or `source ~/.bashrc`) inside the script if you need it.
- **Walltime too short**: job gets `TIMEOUT` killed mid-run. Bump it, but not absurdly — pending priority depends on requested resources.
- **`squeue` shows nothing after sbatch**: the job already finished (or failed instantly). Check `sacct -j <jobid>` and the error file.

## When NOT to use this skill

- On HPC1 (`hpc1login`) — that's LSF, commands are `jsub` / `jjobs` / `jctrl` / `jhist` with `#BSUB` directives.
- On HPC4 (Kunpeng CPU, 910C NPU, or AIStudio). Use that cluster's own instructions.
- For the K8s / AI container workflow on HPC2 — that's a separate path (`/docs/hpc12/k8s/...`), not Slurm.
