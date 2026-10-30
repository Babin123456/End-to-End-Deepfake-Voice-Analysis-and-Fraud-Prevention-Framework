"use client";

import React, { useEffect, useRef } from "react";

interface WaveformVisualizerProps {
  isPlaying: boolean;
  progress: number; // 0.0 to 1.0
}

export default function WaveformVisualizer({ isPlaying, progress }: WaveformVisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animFrameRef = useRef<number | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const barCount = 48;
    let phase = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const width = canvas.width;
      const height = canvas.height;
      const barWidth = width / barCount - 2;

      for (let i = 0; i < barCount; i++) {
        const x = i * (barWidth + 2);
        // Harmonic waveform contour
        const envelope = Math.sin((i / barCount) * Math.PI) * (height * 0.72) + 6;
        const dynamicFactor = isPlaying
          ? Math.sin(phase + i * 0.3) * 0.35 + 0.65
          : 0.45;
        const currentBarHeight = Math.max(4, envelope * dynamicFactor);
        const y = (height - currentBarHeight) / 2;

        const isPlayed = i / barCount <= progress;
        ctx.fillStyle = isPlayed ? "#8ee2b8" : "#223545";
        ctx.beginPath();
        if (typeof ctx.roundRect === "function") {
          ctx.roundRect(x, y, Math.max(1, barWidth), currentBarHeight, 2);
        } else {
          ctx.rect(x, y, Math.max(1, barWidth), currentBarHeight);
        }
        ctx.fill();
      }

      if (isPlaying) {
        phase += 0.18;
      }
      animFrameRef.current = requestAnimationFrame(render);
    };

    render();

    return () => {
      if (animFrameRef.current) {
        cancelAnimationFrame(animFrameRef.current);
      }
    };
  }, [isPlaying, progress]);

  return (
    <div className="waveform-container" aria-label="Audio waveform visualizer">
      <canvas ref={canvasRef} width={420} height={48} className="waveform-canvas" />
    </div>
  );
}
