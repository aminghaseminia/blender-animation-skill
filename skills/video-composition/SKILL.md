---
name: video-composition
description: Assemble, mix, normalize, and validate finished video from Blender, Remotion, Manim, screen capture, and audio sources using FFmpeg and FFprobe — concatenation, overlays, alpha compositing, subtitle burn-in, loudness, fades, speed ramps, GIF/thumbnail export, and platform-specific encodes. Use when combining scenes, fixing mismatched resolutions or frame rates, adding music/voice-over, burning captions, converting formats, or verifying that a rendered file is actually correct.
compatibility: Requires ffmpeg and ffprobe (5.x+ recommended). Check available encoders and filters; builds differ.
metadata:
  domain: video-post-production
  version: "2.1.0"
  engine: ffmpeg
license: MIT
---

# Video Composition — Assembly, Audio, Encoding, Validation

FFmpeg is the delivery layer, not a design tool. It should receive already-designed scenes and produce a clean master plus platform encodes.

Read `references/FFMPEG-COOKBOOK.md` for copy-ready commands and `scripts/validate.sh` for a pre-delivery check.

**Rule zero:** probe first. Building a filter graph against assumed stream properties is the most common cause of broken output.

```bash
ffprobe -v error -show_streams -show_format -of json input.mp4
```

## 1. Normalize before combining

Incompatible inputs cause judder, silence, drift, and halos. Before any multi-source assembly, make every input agree on:

| Property | Target |
|---|---|
| Resolution | project master (e.g. 1920×1080) |
| Pixel aspect ratio | 1:1 |
| Frame rate | project FPS, constant |
| Timebase | consistent |
| Pixel format | `yuv420p` for delivery, `yuva444p10le`/PNG for alpha |
| Color space / transfer | one standard; tag it |
| Audio | 48 kHz, stereo, consistent codec |

```bash
ffmpeg -i in.mp4 -vf "scale=1920:1080:flags=lanczos,fps=30,setsar=1" \
  -c:v libx264 -crf 14 -preset fast -pix_fmt yuv420p \
  -c:a aac -ar 48000 -ac 2 -b:a 256k normalized.mp4
```

Keep intermediates high quality (CRF 12–16 or ProRes). Encode the delivery version once.

## 2. Concatenation

**Same codec, size, fps, pixel format, and audio layout** → stream copy, fast and lossless:

```bash
printf "file 'shot_01.mp4'\nfile 'shot_02.mp4'\n" > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy final.mp4
```

**Anything else** → filter graph:

```bash
ffmpeg -i a.mp4 -i b.mp4 -filter_complex \
  "[0:v]scale=1920:1080,fps=30,setsar=1[v0]; \
   [1:v]scale=1920:1080,fps=30,setsar=1[v1]; \
   [v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 16 -pix_fmt yuv420p -c:a aac final.mp4
```

Never stream-copy concat mismatched inputs. It "succeeds" and produces broken playback.

## 3. Overlay, alpha, and picture-in-picture

```bash
# transparent element over a background
ffmpeg -i bg.mp4 -i logo.mov -filter_complex \
  "[0:v][1:v]overlay=W-w-48:48:format=auto" -c:v libx264 -crf 16 out.mp4

# picture-in-picture, scaled and rounded source
ffmpeg -i main.mp4 -i insert.mp4 -filter_complex \
  "[1:v]scale=640:-2[pip];[0:v][pip]overlay=W-w-40:H-h-40" out.mp4
```

Alpha rules:

- H.264/MP4 cannot carry alpha. Use PNG sequence, ProRes 4444, or WebM/VP9 with alpha.
- Verify the alpha over a contrasting background after every stage.
- Watch for premultiplied-vs-straight alpha halos on dark edges; match the convention of the source renderer.

## 4. Audio

```bash
# music bed with fade in/out and ducking under voice
ffmpeg -i video.mp4 -i music.mp3 -i voice.wav -filter_complex \
  "[1:a]volume=0.35,afade=t=in:st=0:d=1,afade=t=out:st=28:d=2[bed]; \
   [2:a]volume=1.0[vo]; \
   [bed][vo]sidechaincompress=threshold=0.08:ratio=6:attack=8:release=250[duck]; \
   [duck][vo]amix=inputs=2:duration=first:dropout_transition=0[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k out.mp4
```

```bash
# measure loudness, then normalize
ffmpeg -i in.mp4 -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null -
ffmpeg -i in.mp4 -af loudnorm=I=-14:TP=-1:LRA=11 -c:v copy out.mp4
```

Targets vary by destination (-14 LUFS for many web platforms, -23/-24 for broadcast). Measure, then choose. Avoid normalizing a file that is already on target.

## 5. Subtitles

```bash
# burn in (hard subs)
ffmpeg -i in.mp4 -vf "subtitles=captions.srt:force_style='FontName=Inter,FontSize=22,PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BorderStyle=3,Outline=1,Shadow=0'" \
  -c:v libx264 -crf 18 -c:a copy out.mp4

# soft subs (movable track)
ffmpeg -i in.mp4 -i captions.srt -c copy -c:s mov_text -metadata:s:s:0 language=eng out.mp4
```

Check RTL: `force_style` with a shaping-capable font, correct `Alignment`, and a rendered frame inspection. Keep captions inside safe areas and above platform UI.

## 6. Platform encodes

```bash
# landscape YouTube, 1080p30
ffmpeg -i master.mov -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -profile:v high -level 4.1 -movflags +faststart \
  -c:a aac -b:a 192k -ar 48000 out_1080p.mp4

# vertical social, 1080x1920
ffmpeg -i master.mov -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920" \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -movflags +faststart \
  -c:a aac -b:a 192k out_vertical.mp4

# high-quality intermediate for further compositing
ffmpeg -i master.mov -c:v prores_ks -profile:v 3 -pix_fmt yuv422p10le -c:a pcm_s24le master.mov
```

Verify the encoder exists: `ffmpeg -encoders | grep -E "libx264|prores|nvenc"`. Hardware encoders are fast but often lower quality per bit; compare before shipping.

## 7. Frames, contact sheets, GIF

```bash
# stills at times
ffmpeg -ss 00:00:03.5 -i in.mp4 -frames:v 1 frame.png

# contact sheet
ffmpeg -i in.mp4 -vf "fps=1,scale=320:-1,tile=4x4" -frames:v 1 sheet.jpg

# high-quality GIF (palettegen/paletteuse)
ffmpeg -i in.mp4 -vf "fps=15,scale=640:-1:flags=lanczos,palettegen" palette.png
ffmpeg -i in.mp4 -i palette.png -lavfi "fps=15,scale=640:-1:flags=lanczos[x];[x][1:v]paletteuse" out.gif
```

## 8. Validation (do not skip)

```bash
ffprobe -v error \
  -show_entries format=duration,size,bit_rate,format_name \
  -show_entries stream=index,codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,pix_fmt,channels,sample_rate,nb_frames \
  -of json final.mp4
```

Automated checks:

```bash
# black segments (accidental black frames)
ffmpeg -i final.mp4 -vf "blackdetect=d=0.1:pix_th=0.05" -an -f null - 2>&1 | grep blackdetect || true

# frozen segments (too long a static hold)
ffmpeg -i final.mp4 -vf "freezedetect=n=0.003:d=2" -an -f null - 2>&1 | grep freeze || true

# audio presence and peak level
ffmpeg -i final.mp4 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
```

Then inspect first frame, last frame, each transition, and text-heavy frames. Numbers prove the file is well-formed; they do not prove it looks right.

## 9. Frame-accuracy traps

- **VFR sources** (screen recordings, phones) drift against a CFR timeline. Normalize with `fps=30` and check duration.
- **Off-by-one**: N frames at 30 fps is N/30 seconds exactly; a 300-frame render is 10.0 s. If duration is 9.97 s, a frame was dropped.
- **Truncated audio** shorter than video → silence at the end; pad or trim deliberately.
- **Rotated phone video** carries a display matrix; `-noautorotate` only if you really mean it.
- **Color shift** after encode: check `color_primaries`/`transfer` tags; a browser preview is not a reliable colour reference.
- **Repeated encodes** degrade quality; keep a high-quality master and encode from it.

## 10. Delivery package

```text
output/
  final_1080p.mp4          # primary
  final_vertical.mp4       # platform variant, if requested
  final_master.mov         # ProRes/H.264 CRF 14, kept for future encodes
  thumbnail.png            # 1280x720 or 1080x1920
  contact-sheet.jpg
  captions.srt
  project-report.md        # tool versions, settings, checks performed
```

Report exact properties from `ffprobe`; never guess them.
