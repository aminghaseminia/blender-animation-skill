// src/styles/tokens.ts — single source of truth for the visual system.
// Copy into a Remotion project and import everywhere. No literal hex in scenes.

export const palette = {
  bg: "#08090c",
  surface: "#11141a",
  text: "#f2f5f7",
  muted: "#8d97a3",
  accent: "#14c8b1",
  accentSoft: "rgba(20,200,177,0.14)",
  warn: "#ffb347",
  ok: "#3ddc97",
} as const;

export const type = {
  display: 104,
  h1: 72,
  h2: 48,
  body: 30,
  small: 22,
  mono: 24,
} as const;

export const space = (n: number) => n * 8;

export const fontFamily = "Inter, system-ui, -apple-system, sans-serif";
export const monoFamily = "JetBrains Mono, ui-monospace, monospace";

export const safe = {
  horizontal: "6%",
  vertical: "8%",
} as const;
