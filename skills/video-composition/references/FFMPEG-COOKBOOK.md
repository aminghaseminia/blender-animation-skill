# FFmpeg Cookbook — Commands That Actually Run

Companion to `video-composition`. Quote paths; check encoder availability before assuming a codec exists.

```bash
ffmpeg -version
ffmpeg -encoders | grep -E "libx264|libx265|prores|aac|libvpx"
ffmpeg -filters  | grep -E "subtitles|overlay|loudnorm|sidechain"
```

---

## 1. Inspect anything

```bash
# compact overview
ffprobe -v error -show_entries \
format=duration,size,bit_rate,format_name:stream=index,codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,pix_fmt,sample_rate,channels \
-of json input.mp4

# count frames
ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=nb_read_frames -of csv=p=0 input.mp4

# keyframe times
ffprobe -v error -select_streams v:0 -skip_frame nokey \
  -show_entries frame=pts_time -of csv=p=0 input.mp4

# is it variable frame rate?
ffprobe -v error -select_streams v:0 \
  -show_entries stream=r_frame_rate,avg_frame_rate -of default=nw=1 input.mp4
```

`r_frame_rate != avg_frame_rate` usually means VFR. Normalize before editing.

---

## 2. Transcode a clean master

```bash
# H.264 high quality master
ffmpeg -i source.mov -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p \
  -profile:v high -movflags +faststart -c:a aac -b:a 256k -ar 48000 master.mp4

# ProRes intermediate (editing / alpha)
ffmpeg -i source.mov -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le \
  -c:a pcm_s24le master.mov

# alpha intermediate
ffmpeg -i frames/frame_%04d.png -c:v prores_ks -profile:v 4444 \
  -pix_fmt yuva444p10le -c:a pcm_s24le alpha.mov
```

---

## 3. Image sequences

```bash
# PNG sequence → video
ffmpeg -framerate 30 -i renders/frame_%04d.png \
  -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
  -movflags +faststart output.mp4

# video → PNG sequence
ffmpeg -i input.mp4 -vsync 0 frames/frame_%04d.png

# video → high-quality JPEG sequence
ffmpeg -i input.mp4 -q:v 2 frames/frame_%04d.jpg
```

Check for gaps before encoding:

```bash
ls frames/frame_*.png | wc -l
```

A missing frame shifts everything after it. Renumber deliberately with `-start_number` if needed.

---

## 4. Concatenate

```bash
# compatible streams: stream copy
cat > list.txt <<'EOF'
file 'shot_01.mp4'
file 'shot_02.mp4'
file 'shot_03.mp4'
EOF
ffmpeg -f concat -safe 0 -i list.txt -c copy joined.mp4

# incompatible streams: re-encode and normalize
ffmpeg -i a.mp4 -i b.mp4 -filter_complex \
  "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v0]; \
   [1:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v1]; \
   [v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 16 -pix_fmt yuv420p -c:a aac out.mp4
```

With silent clips, generate silence first:

```bash
ffmpeg -f lavfi -i anullsrc=r=48000:cl=stereo -t 3 silence.wav
```

---

## 5. Resize, pad, crop, rotate

```bash
# fit inside 1080p with letterbox
ffmpeg -i in.mp4 -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1" out.mp4

# fill 9:16 with centre crop
ffmpeg -i in.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1" out.mp4

# rotate metadata-aware
ffmpeg -i phone.mov -vf "transpose=1" out.mp4

# scale with sharp downscale
ffmpeg -i 4k.mp4 -vf "scale=1920:1080:flags=lanczos" -c:v libx264 -crf 18 out.mp4
```

---

## 6. Overlay and composite

```bash
# logo top-right with 48 px margin
ffmpeg -i main.mp4 -i logo.png -filter_complex \
  "[0:v][1:v]overlay=W-w-48:48" -c:a copy out.mp4

# lower third from a transparent clip, appearing 4–9 s
ffmpeg -i main.mp4 -i lower.mov -filter_complex \
  "[0:v][1:v]overlay=0:H-h:enable='between(t,4,9)'" -c:v libx264 -crf 16 -c:a copy out.mp4

# split screen
ffmpeg -i left.mp4 -i right.mp4 -filter_complex \
  "[0:v]scale=960:1080[l];[1:v]scale=960:1080[r];[l][r]hstack=inputs=2" out.mp4

# chroma key
ffmpeg -i fg.mp4 -i bg.mp4 -filter_complex \
  "[0:v]chromakey=0x00FF00:0.12:0.05[keyed];[1:v][keyed]overlay" out.mp4
```

`enable='between(t,a,b)'` is evaluated per frame and is the cleanest way to schedule overlays.

---

## 7. Effects used in real deliverables

```bash
# fade in/out video + audio
ffmpeg -i in.mp4 -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=9.5:d=0.5" \
  -af "afade=t=in:st=0:d=0.5,afade=t=out:st=9.5:d=0.5" out.mp4

# speed ramp (2x) with audio pitch correction
ffmpeg -i in.mp4 -filter_complex \
  "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2.0[a]" -map "[v]" -map "[a]" out.mp4

# slow motion 0.5x
ffmpeg -i in.mp4 -filter_complex \
  "[0:v]setpts=2.0*PTS[v];[0:a]atempo=0.5[a]" -map "[v]" -map "[a]" out.mp4

# subtle vignette
ffmpeg -i in.mp4 -vf "vignette=PI/5" -c:a copy out.mp4

# unsharp for screen-capture legibility
ffmpeg -i in.mp4 -vf "unsharp=5:5:0.8:3:3:0.4" out.mp4
```

---

## 8. Audio engineering

```bash
# extract / replace
ffmpeg -i in.mp4 -vn -c:a pcm_s24le audio.wav
ffmpeg -i in.mp4 -i new.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k out.mp4

# normalize a voice track
ffmpeg -i voice.wav -af "highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,loudnorm=I=-16:TP=-1.5:LRA=9" voice_mix.wav

# music bed at -14 dB with 1 s fades
ffmpeg -i music.mp3 -af "volume=-14dB,afade=t=in:st=0:d=1,afade=t=out:st=28:d=2" bed.wav

# duck music under voice
ffmpeg -i voice.wav -i bed.wav -filter_complex \
  "[1:a][0:a]sidechaincompress=threshold=0.05:ratio=8:attack=5:release=200[duck]; \
   [0:a][duck]amix=inputs=2:duration=longest:normalize=0[a]" -map "[a]" mix.wav

# stereo to mono check (phone speakers)
ffmpeg -i mix.wav -ac 1 -ar 48000 mono.wav
```

Always listen to the encoded final on speakers and on a phone-sized device model, not only in headphones.

---

## 9. Subtitles

```bash
# burn in with controlled styling
ffmpeg -i in.mp4 -vf "subtitles=subs.srt:fontsdir=fonts:force_style='FontName=Inter,FontSize=22,PrimaryColour=&H00FFFFFF,BackColour=&H80000000,BorderStyle=3,Outline=1,Shadow=0,MarginV=60'" \
  -c:v libx264 -crf 18 -c:a copy out.mp4

# soft track
ffmpeg -i in.mp4 -i subs.srt -c copy -c:s mov_text -metadata:s:s:0 language=eng out.mp4

# auto-wrap long lines (ASS/libass respects wrapping)
ffmpeg -i in.mp4 -vf "subtitles=subs.srt:force_style='WrapStyle=0,Alignment=2'" out.mp4
```

For Persian/Arabic, pass `fontsdir` containing a shaping-capable font, verify direction in a still, and do not letter-space.

---

## 10. Thumbnail and GIF

```bash
# thumbnail at 3 s, 1280x720
ffmpeg -ss 3 -i final.mp4 -frames:v 1 -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" thumb.png

# animated GIF, 15 fps, 640 px wide
ffmpeg -i final.mp4 -vf "fps=15,scale=640:-1:flags=lanczos,palettegen" palette.png
ffmpeg -i final.mp4 -i palette.png -lavfi "fps=15,scale=640:-1:flags=lanczos[x];[x][1:v]paletteuse" out.gif
```

---

## 11. Quality control

```bash
# black frames
ffmpeg -i final.mp4 -vf "blackdetect=d=0.1:pix_th=0.05" -an -f null - 2>&1 | grep blackdetect || echo "no black segments"

# frozen frames
ffmpeg -i final.mp4 -vf "freezedetect=n=0.003:d=2" -an -f null - 2>&1 | grep freeze || echo "no long freezes"

# audio levels
ffmpeg -i final.mp4 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"

# loudness
ffmpeg -i final.mp4 -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | tail -20

# stream summary
ffprobe -v error -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,channels,sample_rate -of table final.mp4
```

`scripts/validate.sh` wraps these into a single report.

---

## 12. Traps and fixes

| Symptom | Cause | Fix |
|---|---|---|
| Output plays but duration is wrong | VFR source or wrong `-framerate` | Normalize with `fps=30`, verify frame count |
| Audio out of sync after concat | Mixed sample rates / offsets | `-ar 48000 -ac 2` on every input, use filter concat |
| Alpha is black | MP4/H.264 selected | Use PNG sequence or ProRes 4444 |
| Washed-out output | Colour metadata mismatch | Tag colour space, compare a still, avoid double conversion |
| First frame black | Fade-in or encoder preroll | Start fades after frame 0 or trim |
| Subtitles missing | Wrong filter path / font | Quote the path, pass `fontsdir`, test one frame |
| `Unknown encoder 'libx264'` | Build lacks it | Use an available encoder (`ffmpeg -encoders`) or install a full build |
| Huge file | CRF too low / ProRes master shipped | Encode a delivery version at CRF 18–23 |
| Concat produces garbage | Stream-copy on mismatched inputs | Normalize then filter-concat |
