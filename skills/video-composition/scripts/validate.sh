#!/usr/bin/env bash
# Pre-delivery validation for a rendered video.
#
# Usage:
#   ./validate.sh output/final.mp4 [expected_duration_seconds] [expected_fps]
#
# Exit code 0 when all hard checks pass, 2 when something needs attention.
# Read-only: never modifies the input.

set -uo pipefail

FILE="${1:?usage: validate.sh <video> [duration_s] [fps]}"
EXPECT_DUR="${2:-}"
EXPECT_FPS="${3:-}"
FAIL=0

say() { printf '%s\n' "$*"; }
ok()  { printf '  [ok]   %s\n' "$*"; }
bad() { printf '  [FAIL] %s\n' "$*"; FAIL=1; }
warn(){ printf '  [warn] %s\n' "$*"; }

say "== validating: $FILE"

if [ ! -f "$FILE" ]; then
  bad "file does not exist"
  exit 2
fi

SIZE=$(wc -c < "$FILE" | tr -d ' ')
if [ "$SIZE" -lt 1024 ]; then
  bad "file is suspiciously small ($SIZE bytes)"
else
  ok "size: $SIZE bytes"
fi

JSON=$(ffprobe -v error -show_entries \
  format=duration,size,bit_rate:stream=index,codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,pix_fmt,sample_rate,channels,nb_frames \
  -of json "$FILE" 2>/dev/null) || { bad "ffprobe could not read the file"; exit 2; }

DUR=$(printf '%s' "$JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(float(d["format"].get("duration",0)))' 2>/dev/null || echo 0)
say "  duration: ${DUR}s"

if [ -n "$EXPECT_DUR" ]; then
  DIFF=$(python3 -c "print(abs(float('$DUR')-float('$EXPECT_DUR')))")
  if python3 -c "import sys; sys.exit(0 if $DIFF <= 0.05 else 1)"; then
    ok "duration matches expected ${EXPECT_DUR}s"
  else
    bad "duration ${DUR}s differs from expected ${EXPECT_DUR}s by ${DIFF}s"
  fi
fi

# stream table
printf '%s' "$JSON" | python3 -c '
import json,sys
d=json.load(sys.stdin)
for s in d["streams"]:
    t=s.get("codec_type")
    if t=="video":
        print("  video: %s %sx%s %s fps pix=%s frames=%s" % (
            s.get("codec_name"), s.get("width"), s.get("height"),
            s.get("r_frame_rate"), s.get("pix_fmt"), s.get("nb_frames","?")))
    elif t=="audio":
        print("  audio: %s %s Hz %sch" % (
            s.get("codec_name"), s.get("sample_rate"), s.get("channels")))
    else:
        print("  %s: %s" % (t, s.get("codec_name")))
'
VCODEC=$(printf '%s' "$JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(next((s.get("codec_name") for s in d["streams"] if s.get("codec_type")=="video"), ""))')
ACODEC=$(printf '%s' "$JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(next((s.get("codec_name") for s in d["streams"] if s.get("codec_type")=="audio"), ""))')

[ -n "$VCODEC" ] && ok "video stream present ($VCODEC)" || bad "no video stream"
if [ -z "$ACODEC" ]; then
  warn "no audio stream (fine only if the project is intentionally silent)"
else
  ok "audio stream present ($ACODEC)"
fi

# fps
FPS=$(printf '%s' "$JSON" | python3 -c 'import json,sys; d=json.load(sys.stdin); s=next((s for s in d["streams"] if s.get("codec_type")=="video"),{}); r=s.get("avg_frame_rate") or s.get("r_frame_rate") or "0/0"; n,dd=(r.split("/")+["1"])[:2]; print(round(float(n)/float(dd or 1),2))')
if [ -n "$EXPECT_FPS" ]; then
  if python3 -c "import sys; sys.exit(0 if abs($FPS-float('$EXPECT_FPS'))<0.05 else 1)"; then
    ok "fps $FPS matches expected $EXPECT_FPS"
  else
    bad "fps $FPS differs from expected $EXPECT_FPS"
  fi
else
  say "  fps: $FPS"
fi

# black segments
BLACK=$(ffmpeg -hide_banner -i "$FILE" -vf "blackdetect=d=0.1:pix_th=0.05" -an -f null - 2>&1 | grep -c blackdetect || true)
if [ "${BLACK:-0}" -gt 0 ]; then
  warn "$BLACK black segment(s) detected — inspect whether intentional"
else
  ok "no black segments detected"
fi

# long freezes (static holds > 2 s)
FREEZE=$(ffmpeg -hide_banner -i "$FILE" -vf "freezedetect=n=0.003:d=2" -an -f null - 2>&1 | grep -c freeze || true)
if [ "${FREEZE:-0}" -gt 0 ]; then
  warn "$FREEZE long freeze event(s) detected — confirm intentional hold"
else
  ok "no long freezes detected"
fi

# audio peak
if [ -n "$ACODEC" ]; then
  PEAK=$(ffmpeg -hide_banner -i "$FILE" -af volumedetect -f null - 2>&1 | awk -F': ' '/max_volume/ {print $2}' | tail -1)
  if [ -n "$PEAK" ]; then
    say "  audio peak: $PEAK"
    case "$PEAK" in
      -*[0-9]*) : ;;
      *) warn "peak may be clipping" ;;
    esac
  fi
fi

say ""
if [ "$FAIL" -eq 0 ]; then
  say "RESULT: technical checks passed. Visual inspection still required."
  exit 0
else
  say "RESULT: FAILED — fix the items marked [FAIL]."
  exit 2
fi
