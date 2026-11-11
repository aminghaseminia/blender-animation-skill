#!/usr/bin/env bash
# Render helper for Blender projects built with the motion-studio conventions.
#
# Usage:
#   ./render.sh preview <scene.blend> [start] [end]
#   ./render.sh final   <scene.blend> [start] [end]
#   ./render.sh encode  <frames-dir> <fps> <out.mp4>
#
# Env:
#   BLENDER=/path/to/blender   (default: blender)

set -euo pipefail

BLENDER="${BLENDER:-blender}"
MODE="${1:-preview}"
shift || true

case "$MODE" in
  preview|final)
    BLEND="${1:?scene.blend required}"
    START="${2:-1}"
    END="${3:-300}"
    DIR="$(cd "$(dirname "$BLEND")" && pwd)"
    OUT="$DIR/renders/${MODE}"
    mkdir -p "$OUT" "$DIR/logs"

    if [ "$MODE" = "preview" ]; then
      # 50% resolution via a temporary expression, EEVEE if available.
      "$BLENDER" -b "$BLEND" \
        --python-expr "import bpy; s=bpy.context.scene; s.render.resolution_percentage=50" \
        -o "$OUT/frame_####" -F PNG -f "$START-$END" \
        2>&1 | tee "$DIR/logs/preview_${START}_${END}.log"
    else
      "$BLENDER" -b "$BLEND" -o "$OUT/frame_####" -F PNG -f "$START-$END" \
        2>&1 | tee "$DIR/logs/final_${START}_${END}.log"
    fi

    COUNT=$(find "$OUT" -name 'frame_*.png' | wc -l | tr -d ' ')
    EXPECTED=$((END - START + 1))
    echo "[render] frames $COUNT / $EXPECTED in $OUT"
    if [ "$COUNT" -ne "$EXPECTED" ]; then
      echo "[render] ERROR: missing frames" >&2
      exit 2
    fi
    ;;

  encode)
    DIR="${1:?frames dir required}"
    FPS="${2:-30}"
    OUT="${3:-final.mp4}"
    ffmpeg -y -framerate "$FPS" -i "$DIR/frame_%04d.png" \
      -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
      -movflags +faststart "$OUT"
    ffprobe -v error -show_entries format=duration,size \
      -show_entries stream=width,height,r_frame_rate,codec_name -of json "$OUT"
    ;;

  *)
    echo "usage: $0 {preview|final|encode} ..." >&2
    exit 1
    ;;
esac
