#!/bin/bash
# Download the open-access papers in download_list.tsv into papers/<theme>/.
# macOS/Linux, needs only bash + curl. Same sources and order as fetch_papers.py:
# arXiv PDF -> Europe PMC PDF -> Europe PMC full-text XML -> open-access URL.
# Writes download_log.csv (also the record of papers we could not access).
cd "$(dirname "$0")" || exit 1
UA="GP-RareLink-background-fetch/1.0 (Rare Genomics Institute)"
LOG=download_log.csv
TODAY=$(date +%Y-%m-%d)
echo "key,theme,status,file,source,date" > "$LOG"
ok=0; fail=0; have=0
while IFS=$'\t' read -r key theme rest; do
  [ -z "$key" ] && continue
  mkdir -p "papers/$theme"
  if [ -s "papers/$theme/$key.pdf" ] || [ -s "papers/$theme/$key.xml" ]; then
    echo "$key,$theme,already_present,,,$TODAY" >> "$LOG"; have=$((have+1)); continue
  fi
  done_one=""
  IFS=$'\t' read -ra cands <<< "$rest"
  for c in "${cands[@]}"; do
    kind="${c%%|*}"; url="${c#*|}"
    tmp="papers/$theme/.$key.part"
    if curl -sSL -f -m 120 -A "$UA" -o "$tmp" "$url" 2>/dev/null; then
      magic=$(head -c 5 "$tmp")
      if [ "$kind" = pdf ] && [ "$magic" = "%PDF-" ]; then
        mv "$tmp" "papers/$theme/$key.pdf"; done_one="papers/$theme/$key.pdf"
      elif [ "$kind" = xml ] && [ "${magic:0:1}" = "<" ]; then
        mv "$tmp" "papers/$theme/$key.xml"; done_one="papers/$theme/$key.xml"
      fi
    fi
    rm -f "$tmp"
    sleep 1
    if [ -n "$done_one" ]; then
      echo "$key,$theme,downloaded,$done_one,$url,$TODAY" >> "$LOG"; echo "ok    $key"; ok=$((ok+1)); break
    fi
  done
  if [ -z "$done_one" ]; then
    echo "$key,$theme,failed,,,$TODAY" >> "$LOG"; echo "FAIL  $key"; fail=$((fail+1))
  fi
done < download_list.tsv
echo ""
echo "downloaded $ok, already present $have, failed $fail. Details in $LOG"
