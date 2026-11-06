#!/usr/bin/env python3
"""Print the facts of one monitored run, what changed since the last check, and EVENTS."""
import glob, json, os, re, subprocess, sys, time
from datetime import datetime, timezone

HOME = os.environ.get("MONITOR_HOME", os.path.expanduser("~/.claude/monitor-autoresearch"))
CMUX = "/Applications/cmux.app/Contents/Resources/bin/cmux"
IDLE_MIN = 20
STEP_BACK_MIN = 60
CRON_RENEW_DAYS = 6


def sh(cmd, cwd=None, timeout=60):
    try:
        r = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str), capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip()
    except (subprocess.TimeoutExpired, OSError) as e:
        return 1, str(e)


def records(repo):
    out = {}
    for f in glob.glob(f"{repo}/records/*.md"):
        head = open(f, errors="replace").read().split("+++")
        if len(head) < 3:
            continue
        r = {k: v.strip().strip('"') for k, v in re.findall(r"^(\w+)\s*=\s*(.+)$", head[1], re.M)}
        r["lead"] = " ".join(head[2].split())[:220]
        out[os.path.basename(f)[:-3]] = r
    return out


def score(r):
    try:
        return float(r.get("score", ""))
    except ValueError:
        return None


def rollouts(repo, days=3):
    """Codex rollout files of this repository, newest first."""
    now, found = time.time(), []
    for d in range(days):
        day = time.strftime("%Y/%m/%d", time.localtime(now - d * 86400))
        found += glob.glob(os.path.expanduser(f"~/.codex/sessions/{day}/rollout-*.jsonl"))
    out = []
    for f in sorted(found, key=os.path.getmtime, reverse=True):
        try:
            meta = json.loads(open(f).readline()).get("payload", {})
        except (OSError, ValueError):
            continue
        if meta.get("cwd") == repo:
            out.append((f, "parent_thread_id" not in meta))
    return out


def tail(f, n=200_000):
    with open(f, "rb") as h:
        h.seek(max(0, os.path.getsize(f) - n))
        return h.read().decode(errors="replace")


def last_messages(f, n=2):
    msgs = []
    for line in tail(f).splitlines():
        try:
            d = json.loads(line)
        except ValueError:
            continue
        p = d.get("payload", {})
        if d.get("type") == "response_item" and p.get("type") == "message" and p.get("role") == "assistant":
            text = " ".join(c.get("text", "") for c in p.get("content", []) if isinstance(c, dict)).strip()
            if text:
                msgs.append(" ".join(text.split())[:400])
    return msgs[-n:]


def main():
    name = sys.argv[1]
    base = f"{HOME}/{name}"
    run = json.load(open(f"{base}/run.json"))
    repo = run["repo"]
    state_file = f"{base}/state.json"
    state = json.load(open(state_file)) if os.path.exists(state_file) else {}
    now = time.time()
    events = []

    # Agent
    code, screen = sh([CMUX, "read-screen", "--workspace", run["workspace"], "--lines", "40"])
    files = rollouts(repo)
    mains = [f for f, is_main in files if is_main]
    ages = [(now - os.path.getmtime(f)) / 60 for f, _ in files]
    active = sum(a < 15 for a in ages)
    newest = min(ages) if ages else None
    limit = re.search(r"usage limit.{0,120}?try again at ([^\".\\]+)", " ".join(tail(f) for f in mains[:3]))
    print(f"AGENT: screen {'ok' if code == 0 else 'unreadable'}; "
          f"last activity {'none' if newest is None else f'{newest:.0f} min ago'}; {active} threads active in 15 min")
    for m in last_messages(mains[0]) if mains else []:
        print("  >", m)
    if code != 0:
        events.append("AGENT_GONE")
    elif re.search(r"\b\d+ question", screen):
        events.append("QUESTION")
    if limit and newest is not None and newest < 7 * 1440 and state.get("limit_seen") != limit.group(1):
        events.append(f"USAGE_LIMIT reset: {limit.group(1).strip()}")
    if limit:
        state["limit_seen"] = limit.group(1)
    if code == 0 and "Working" not in screen and (newest is None or newest > IDLE_MIN):
        events.append("AGENT_IDLE")

    # Git
    head = sh(["git", "rev-parse", "HEAD"], repo)[1]
    last = state.get("head")
    new = sh(["git", "log", "--oneline", f"{last}..HEAD"], repo)[1].splitlines() if last and last != head else []
    dirty = len(sh(["git", "status", "--porcelain"], repo)[1].splitlines())
    print(f"GIT: {len(new)} new commits; {dirty} uncommitted paths")
    for c in new[:15]:
        print("  ", c[:110])

    # Records
    recs = records(repo)
    seen = set(state.get("records", []))
    fresh = sorted(set(recs) - seen) if seen else []
    trials = {k: r for k, r in recs.items() if k.startswith("T")}
    scored = sorted(((score(r), k) for k, r in trials.items() if score(r) is not None), reverse=True)
    best = scored[0][0] if scored else None
    print(f"RECORDS: {len(recs)} total; {len(fresh)} new")
    for k, r in [(k, recs[k]) for k in fresh[:15]]:
        print(f"  {k} [{r.get('status', '')}] score={r.get('score', '-')} holdout={r.get('holdout', '-')} {r.get('title', '')[:90]}")
        print(f"     {r['lead']}")
    print("BEST:", ", ".join(
        f"{k} {s:g} (holdout {recs[k].get('holdout', '-')}, {recs[k].get('title', '')[:50]})" for s, k in scored[:3]) or "none")
    prior = state.get("best")
    results = {k: [r.get("score"), r.get("holdout")] for k, r in trials.items()}
    was = state.get("results")
    changed = sorted(k for k, v in results.items() if was is not None and v != was.get(k) and any(v))
    ties = [k for k in changed if prior is not None and (score(recs[k]) or -1) >= prior]
    if ties:
        events.append("NEW_BEST " + " ".join(ties))
    rest = [k for k in changed if k not in ties]
    if rest:
        events.append("NEW_SCORE " + " ".join(rest))
    ideas = [k for k in fresh if k in trials and recs[k].get("kind") == "new"]
    if ideas:
        events.append("NEW_IDEA " + " ".join(ideas))
    dropped = [k for k in fresh if k[0] == "X" or (k[0] == "T" and recs[k].get("status") == "closed")]
    if dropped:
        events.append("NEW_DROPPED " + " ".join(dropped))
    for prefix, every in (("F", 5), ("S", 10)):
        dates = [r.get("created", "") for k, r in recs.items() if k.startswith(prefix)]
        since = sum(r.get("created", "") > max(dates, default="") for r in trials.values())
        print(f"{prefix}: {since} trials since the last one (every {every})")

    # Compute
    if run.get("compute_status"):
        code, status = sh(run["compute_status"], timeout=90)
        print("COMPUTE:", status[:600] if code == 0 else f"status failed: {status[:200]}")

    # Staying alive
    if sh(["pgrep", "-x", "caffeinate"])[0] != 0:
        events.append("AWAKE_LOST")
    created = run.get("cron_created")
    if created:
        age = datetime.now(timezone.utc) - datetime.fromisoformat(created).astimezone(timezone.utc)
        if age.days >= CRON_RENEW_DAYS:
            events.append("CRON_RENEW")
    if now - state.get("step_back", 0) > STEP_BACK_MIN * 60:
        events.append("STEP_BACK")
        state["step_back"] = now

    print("EVENTS:", "; ".join(events) or "none")
    state.update(head=head, records=sorted(recs), best=best, results=results, checked=now)
    json.dump(state, open(state_file, "w"))


if __name__ == "__main__":
    main()
