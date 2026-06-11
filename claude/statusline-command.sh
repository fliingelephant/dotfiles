#!/bin/bash
# Claude Code status line: dir | git branch [wt:name] | model effort | context used/size pct% | 5h pct% →reset | 7d pct%
# Input schema: https://code.claude.com/docs/en/statusline.md
input=$(cat)

# one value per line: empty lines survive `read`, unlike empty @tsv fields under tab-IFS
{ read -r dir; read -r model; read -r effort; read -r ctx_used; read -r ctx_pct; read -r ctx_size; read -r five; read -r five_reset; read -r week; } <<<"$(jq -r '
  (.workspace.current_dir // .cwd // ""),
  (.model.display_name // ""),
  (.effort.level // ""),
  (.context_window.total_input_tokens // 0),
  (.context_window.used_percentage // ""),
  (.context_window.context_window_size // 200000),
  (.rate_limits.five_hour.used_percentage // ""),
  (.rate_limits.five_hour.resets_at // ""),
  (.rate_limits.seven_day.used_percentage // "")
' <<<"$input")"

RST=$'\033[0m'; DIM=$'\033[2m'; CYAN=$'\033[36m'; GREEN=$'\033[32m'; MAG=$'\033[35m'; BLUE=$'\033[34m'

pct_color() { awk -v p="$1" 'BEGIN{ printf "\033[%sm", (p<50 ? "32" : (p<80 ? "33" : "31")) }'; }

dir_disp="$dir"
case "$dir" in "$HOME"*) dir_disp="~${dir#"$HOME"}";; esac
segs=("${CYAN}${dir_disp}${RST}")

branch=$(git -C "$dir" symbolic-ref --short -q HEAD 2>/dev/null || git -C "$dir" rev-parse --short HEAD 2>/dev/null)
if [ -n "$branch" ]; then
  wt=""
  { read -r git_dir; read -r common_dir; } <<<"$(git -C "$dir" rev-parse --git-dir --git-common-dir 2>/dev/null)"
  [ "$git_dir" != "$common_dir" ] && wt=" ${MAG}[wt:${git_dir##*/}]${RST}"
  segs+=("${GREEN}⎇ ${branch}${RST}${wt}")
fi

if [ -n "$model" ]; then
  [ -n "$effort" ] && model+=" ${DIM}${effort}"
  segs+=("${BLUE}${model}${RST}")
fi

if [ -n "$ctx_pct" ]; then
  used_h=$(awk -v n="$ctx_used" 'BEGIN{ if (n>=1e6) printf "%.1fM", n/1e6; else if (n>=1e3) printf "%.0fk", n/1e3; else printf "%d", n }')
  size_h=$(awk -v n="$ctx_size" 'BEGIN{ if (n>=1e6) printf "%.0fM", n/1e6; else printf "%.0fk", n/1e3 }')
  segs+=("context $(pct_color "$ctx_pct")${used_h}/${size_h} ${ctx_pct%%.*}%${RST}")
fi

if [ -n "$five" ]; then
  reset=""
  [ -n "$five_reset" ] && reset=" ${DIM}→$(date -r "$five_reset" +%H:%M)${RST}"
  segs+=("5h $(pct_color "$five")${five%%.*}%${RST}${reset}")
fi
[ -n "$week" ] && segs+=("7d $(pct_color "$week")${week%%.*}%${RST}")

out="${segs[0]}"
for s in "${segs[@]:1}"; do out+=" ${DIM}|${RST} ${s}"; done
printf '%s' "$out"
