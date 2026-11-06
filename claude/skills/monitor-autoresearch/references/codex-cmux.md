# Driving Codex in cmux


`cmux` is `/Applications/cmux.app/Contents/Resources/bin/cmux`.

- Read: `cmux read-screen --workspace <ws> --lines 60`
- Send: `cmux send --workspace <ws> "<one line>"`, then
  `cmux send-key --force --workspace <ws> enter`. Confirm on screen that it landed.
- Open question ("? N question"): read it from the newest rollout in
  `~/.codex/sessions/`, then `cmux send-key --workspace <ws> shift+left`. Arrow
  keys pick an option. For a custom answer pick "Other", then
  `cmux send --force` and `send-key --force enter`.
- `STATE.md` questions: answer by a note. The agent owns that file.
- Usage limit text: "You've hit your usage limit ... try again at <date>."
- Workspace gone: `cmux new-workspace --name "<name>" --cwd <repo> --command '<launch>'`
