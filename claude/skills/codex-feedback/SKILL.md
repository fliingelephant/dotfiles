---
name: codex-feedback
description: Check Codex review feedback on the current branch's PR. Shows processing status, review comments for discussion, or confirms PR is clean.
---

# Codex Feedback

Check the latest Codex review status on the current branch's PR.

## Step 1: Find the PR

```bash
gh pr view --json number,url -q '.number'
```
If no PR exists, tell the user.

## Step 2: Determine status

Check in this order:

1. **Latest `@codex review` trigger comment** — check if 👀 (eyes) reaction is present and no newer review or "no issues" comment exists. If so, Codex is still processing.

2. **"No major issues" comment** (posted as an issue comment by `chatgpt-codex-connector[bot]`):
   ```bash
   gh api "repos/{owner}/{repo}/issues/{pr}/comments" \
     --jq '[.[] | select(.user.login == "chatgpt-codex-connector[bot]") | select(.body | test("Didn.t find any major issues"))] | last'
   ```
   If this is newer than the latest review, the PR is refined.

3. **Latest review with comments** — fetch the most recent Codex review and its inline comments.

## Step 3: Present results

### If still processing
> Codex is still reviewing. Check back in a few minutes.

### If clean
> Codex: no major issues found. PR is refined.

### If review comments found

Present **every** comment clearly. For each comment:

- **File and priority**: e.g. `src/vmc/workflow.py (P1)`
- **Summary**: One sentence describing the issue in plain language
- **Detail**: The essential concern — what breaks, what's wrong, what's the risk

Format as a numbered list. Example:

---

**Codex review complete** (review XXXX). N comments:

1. **`path/to/file.py` (P2): Short title**
   Summary of the concern. What the code does, what the reviewer thinks is wrong, what the risk is.

2. **`another/file.py` (P1): Short title**
   Summary...

---

After presenting, ask: **"What do you think?"**

**Do not skip, dismiss, or pre-judge any comments.** Do not say "same as before" or "let it crash" without presenting the content first. The user decides what to fix, not the assistant.

## Step 4: Resolve fixed comments

After the user confirms a comment has been **fixed** (code changed and committed), resolve its thread on GitHub:

```bash
gh api graphql -f query='mutation {
  resolveReviewThread(input: {threadId: "<thread_node_id>"}) {
    thread { isResolved }
  }
}'
```

To get review thread IDs (note: use `PRRT_*` thread IDs, not `PRRC_*` comment IDs):
```bash
gh api graphql -f query='query { repository(owner: "{owner}", name: "{repo}") {
  pullRequest(number: {pr}) { reviewThreads(last: 20) { nodes {
    id isResolved comments(first: 1) { nodes { body } }
  } } }
}' --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved == false) | {id, body: .comments.nodes[0].body[:80]}'
```

**Only resolve comments that were actually fixed.** Leave skipped/deferred comments unresolved for the user to handle manually.
