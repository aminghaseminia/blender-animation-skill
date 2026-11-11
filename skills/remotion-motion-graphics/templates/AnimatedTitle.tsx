// src/components/AnimatedTitle.tsx
// Deterministic entrance: opacity + rise + tracking settle. No timers, no randomness.

import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { fontFamily, palette } from "../styles/tokens";

export const AnimatedTitle: React.FC<{
  text: string;
  delay?: number;
  size?: number;
  color?: string;
  align?: "left" | "center" | "right";
  maxWidth?: number | string;
}> = ({ text, delay = 0, size = 96, color = palette.text, align = "left", maxWidth }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const local = frame - delay;
  const enter = spring({
    frame: local,
    fps,
    config: { damping: 20, stiffness: 140, mass: 0.9 },
  });
  const opacity = interpolate(local, [0, 10], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const tracking = interpolate(enter, [0, 1], [0.14, -0.02]);

  return (
    <div
      style={{
        fontFamily,
        fontSize: size,
        fontWeight: 600,
        lineHeight: 1.05,
        letterSpacing: `${tracking}em`,
        color,
        opacity,
        textAlign: align,
        maxWidth,
        transform: `translateY(${(1 - enter) * 28}px) scale(${0.97 + enter * 0.03})`,
        willChange: "transform, opacity",
      }}
    >
      {text}
    </div>
  );
};
