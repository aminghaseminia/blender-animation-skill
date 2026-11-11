# Quality Checklist — The Gate Before "Done"

Reference for `motion-studio`. Do not declare completion until every applicable item passes or is explicitly reported as unverified.

## 1. Technical

```bash
ffprobe -v error \
  -show_entries format=duration,size,bit_rate \
  -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,pix_fmt,channels,sample_rate,nb_frames \
  -of json output/final.mp4
```

- [ ] File exists and is non-zero.
- [ ] Opens and plays in a normal player.
- [ ] Duration matches the brief within ~1 frame.
- [ ] Frame count matches `duration × fps`.
- [ ] Width/height and aspect ratio are correct.
- [ ] Frame rate is constant and matches the pipeline.
- [ ] Video codec/pixel format are delivery-appropriate (`h264`/`yuv420p` for broad compatibility).
- [ ] Audio stream exists if required, at 48 kHz, correct channel count.
- [ ] No missing frames in any image sequence.
- [ ] No truncated or corrupt tail.
- [ ] Alpha preserved if transparency was required (verify visually, not by extension).

## 2. Automated artifact checks

```bash
# accidental black segments
ffmpeg -i output/final.mp4 -vf "blackdetect=d=0.1:pix_th=0.05" -an -f null - 2>&1 | grep blackdetect || true

# unintended long freezes
ffmpeg -i output/final.mp4 -vf "freezedetect=n=0.003:d=2" -an -f null - 2>&1 | grep freeze || true

# audio peak / loudness
ffmpeg -i output/final.mp4 -af volumedetect -f null - 2>&1 | grep -E "mean_volume|max_volume"
```

- [ ] Every reported black segment is intentional (a designed cut to black).
- [ ] No freeze longer than intended.
- [ ] No clipping; loudness appropriate to the destination.
- [ ] No digital silence where sound should exist.

## 3. Visual

Inspect actual frames: 0, each scene start/end, each transition midpoint, text-heavy frames, action peaks, last frame.

- [ ] First frame is intentional (not a preroll blank).
- [ ] Last frame is intentional (logo settled, CTA readable).
- [ ] No one-frame flashes, gaps, or jumps at boundaries.
- [ ] No flicker, z-fighting, texture swimming, popping, or intersecting geometry.
- [ ] No clipped faces, hats, or type at frame edges.
- [ ] Colour and exposure are consistent scene to scene.
- [ ] No accidental letterbox/pillarbox; safe areas respected.
- [ ] Masks/alpha edges are clean, with no dark or white halos.
- [ ] Motion blur is present only where intended.

## 4. Typography and content

- [ ] Copy is exactly as approved (punctuation, capitalisation, numbers).
- [ ] Every glyph renders; no tofu boxes or fallback fonts.
- [ ] RTL scripts shape correctly and are not letter-spaced.
- [ ] Mixed RTL/LTR punctuation and numbers read correctly.
- [ ] Text is legible at the intended playback size, including on a phone.
- [ ] Line breaks are intentional; no orphan words.
- [ ] Dwell time is sufficient to read without pausing.
- [ ] A cap-height check at the smallest platform crop still passes.

## 5. Motion craft

- [ ] One focal point per beat; hierarchy is obvious.
- [ ] Timing feels intentional, with a rest before the payoff.
- [ ] Easing is varied appropriately, not one curve everywhere.
- [ ] Transitions express a relationship and are consistent.
- [ ] Camera movement has a reason.
- [ ] Nothing moves continuously "because it can".
- [ ] Effects serve message, depth, hierarchy, or rhythm.

## 6. Audio

- [ ] Synchronized at the first and last sound event.
- [ ] Voice intelligible over music.
- [ ] No clicks at cuts, fades on every boundary.
- [ ] Stereo/mono balance acceptable on a phone.
- [ ] Music/SFX licences documented and compatible with use.
- [ ] Final mix checked on the encoded file, not the timeline.

## 7. Portability and editability

- [ ] Source project opens from a fresh session.
- [ ] Paths are relative or documented.
- [ ] External fonts/plugins/assets are listed in the README or manifest.
- [ ] Versions and exact commands are documented.
- [ ] Rerender works without undocumented local state.
- [ ] Lockfiles committed where applicable.
- [ ] The last good render is preserved until the replacement passes.

## 8. Delivery

- [ ] Final media in `output/` with a clear name.
- [ ] Editable source delivered.
- [ ] Asset manifest with source/licence.
- [ ] README: install, preview, render, revise.
- [ ] `project-report.md` with real measured properties.
- [ ] Residual QA or unverified items stated plainly.

## 9. Honesty clause

If you could not inspect the video visually, say so. A checklist with unchecked visual items is honest; a claim of "looks great" without inspection is not.

```text
Verified: file specs, duration, black/freeze detection, audio presence.
Not verified: visual composition of scene 4, because no frame inspection
capability was available. Please review 00:07–00:11 before publishing.
```
