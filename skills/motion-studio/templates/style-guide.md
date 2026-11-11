# Style Guide — {{PROJECT}}

Locked before mass production. Every scene imports these values; no scene invents its own.

## Colour

| Role | Hex | Usage |
|---|---|---|
| Background | `#08090C` | full-bleed base |
| Surface | `#11141A` | panels, cards |
| Text primary | `#F2F5F7` | headlines, body |
| Text muted | `#8D97A3` | captions, sources |
| Accent | `#14C8B1` | ≤10% of frame, one idea |
| Semantic warn | `#FFB347` | errors, emphasis |
| Semantic ok | `#3DDC97` | success states |

Rules:

- One accent colour per piece unless a second encodes meaning.
- Contrast: body ≥ 4.5:1; large text/graphics ≥ 3:1.
- Verify colour after encode, not only in the preview.

## Typography

| Role | Family | Weight | Size @1080p | Tracking | Line height |
|---|---|---|---|---|---|
| Display | | 600 | 96–104 | -2% | 1.05 |
| H1 | | 600 | 72 | -1.5% | 1.1 |
| H2 | | 500 | 48 | -1% | 1.2 |
| Body | | 400 | 30 | 0 | 1.45 |
| Label | | 500 | 22 (uppercase) | +12% | 1.2 |
| Mono | | 400 | 24 | 0 | 1.4 |

Notes:

- Fonts licensed for video/embedding: `yes / no`
- RTL font: `__________` (shaping verified: `yes / no`)
- Minimum on-screen text size at delivery: `22 px @1080p`

## Grid and spacing

```text
Columns     12
Margin      5–8% (vertical: 8–10% sides, 12% top, 18% bottom)
Base unit   8 px
Gaps        8 / 16 / 24 / 40 / 64
Radius      0 / 4 / 8 / 16 (pick one language)
Stroke      1.5–2 px for hairlines at 1080p
```

## Shape and surface

- Flat / soft-lit / bevelled: `__________`
- Shadows: `none / subtle / dramatic`
- Glow: `only on emissive accents`
- Texture: `none / procedural grain / footage`

## Motion language

| Action | Duration | Easing |
|---|---|---|
| Enter headline | 14 f | ease-out cubic |
| Exit | 10 f | ease-in cubic |
| Move between rest states | 18 f | ease-in-out |
| Spring pop | — | damping 18, stiffness 120 |
| Camera move | 60–120 f | soft ease-in-out |

Transition vocabulary: `cut`, `8 f crossfade`, `left wipe`. Nothing else without a reason.

## Sound

| Role | Description | Level |
|---|---|---|
| Bed | minimal pulse | -18 dB under voice |
| Accent | tick / soft impact | -12 dB |
| Voice | dry, close | -16 LUFS target |
| Silence | 0.5 s before final reveal | — |

## Logo and brand rules

- Clear space: `___ × logo height`
- Minimum size: `___ px wide`
- Do not recolour / stretch / add effects unless the brand guide allows it.
- End card duration: `≥ 2 s`.
