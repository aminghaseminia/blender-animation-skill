// src/compositions/MainVideo.tsx
// Three-scene skeleton with explicit frame math. Replace scene contents.

import React from "react";
import { AbsoluteFill, Series, staticFile, Audio } from "remotion";
import { AnimatedTitle } from "../components/AnimatedTitle";
import { palette, safe } from "../styles/tokens";

const Intro: React.FC = () => (
  <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
    <AnimatedTitle text="Build faster" size={104} align="center" />
  </AbsoluteFill>
);

const Body: React.FC = () => (
  <AbsoluteFill
    style={{
      justifyContent: "center",
      padding: `${safe.vertical} ${safe.horizontal}`,
    }}
  >
    <AnimatedTitle text="One pipeline. Every frame reproducible." size={64} delay={12} />
  </AbsoluteFill>
);

const Outro: React.FC = () => (
  <AbsoluteFill style={{ justifyContent: "center", alignItems: "center" }}>
    <AnimatedTitle text="MOTION STUDIO" size={72} delay={6} align="center" />
  </AbsoluteFill>
);

export const MainVideo: React.FC = () => (
  <AbsoluteFill style={{ backgroundColor: palette.bg }}>
    <Series>
      <Series.Sequence durationInFrames={90}>
        <Intro />
      </Series.Sequence>
      <Series.Sequence durationInFrames={180}>
        <Body />
      </Series.Sequence>
      <Series.Sequence durationInFrames={90}>
        <Outro />
      </Series.Sequence>
    </Series>

    {/* Optional bed: fades are handled inside a dedicated audio component. */}
    <Audio src={staticFile("audio/bed.mp3")} volume={0.4} />
  </AbsoluteFill>
);
