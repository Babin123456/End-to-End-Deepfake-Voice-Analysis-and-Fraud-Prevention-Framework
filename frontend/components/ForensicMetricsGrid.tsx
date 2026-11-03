"use client";

import React from "react";

interface ForensicBreakdown {
  spectral_consistency?: number;
  pitch_naturalness?: number;
  vocoder_artifact_score?: number;
}

interface AcousticFeatures {
  duration_seconds?: number;
  sample_rate?: number;
  channels?: number;
  snr_db?: number | null;
  fundamental_frequency_hz?: number | null;
}

interface ForensicMetricsGridProps {
  breakdown?: ForensicBreakdown;
  features?: AcousticFeatures;
}

export default function ForensicMetricsGrid({ breakdown, features }: ForensicMetricsGridProps) {
  const spectral = breakdown?.spectral_consistency ?? 85.0;
  const pitch = breakdown?.pitch_naturalness ?? 90.0;
  const vocoder = breakdown?.vocoder_artifact_score ?? 12.0;
  const snr = features?.snr_db ?? null;

  return (
    <div className="forensic-grid" role="region" aria-label="Forensic metrics breakdown">
      <div className="metric-card">
        <div className="metric-header">
          <span>Pitch Naturalness</span>
          <strong className={pitch >= 70 ? "text-safe" : "text-danger"}>
            {pitch.toFixed(1)}%
          </strong>
        </div>
        <div className="metric-bar-track">
          <div
            className={`metric-bar-fill ${pitch >= 70 ? "fill-safe" : "fill-danger"}`}
            style={{ width: `${Math.max(5, Math.min(100, pitch))}%` }}
          />
        </div>
        <span className="metric-hint">Biological vocal cord micro-tremors</span>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span>Spectral Consistency</span>
          <strong className={spectral >= 65 ? "text-safe" : "text-warning"}>
            {spectral.toFixed(1)}%
          </strong>
        </div>
        <div className="metric-bar-track">
          <div
            className={`metric-bar-fill ${spectral >= 65 ? "fill-safe" : "fill-warning"}`}
            style={{ width: `${Math.max(5, Math.min(100, spectral))}%` }}
          />
        </div>
        <span className="metric-hint">Frequency envelope coherence</span>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span>Vocoder Artifacts</span>
          <strong className={vocoder < 30 ? "text-safe" : "text-danger"}>
            {vocoder.toFixed(1)}%
          </strong>
        </div>
        <div className="metric-bar-track">
          <div
            className={`metric-bar-fill ${vocoder < 30 ? "fill-safe" : "fill-danger"}`}
            style={{ width: `${Math.max(5, Math.min(100, vocoder))}%` }}
          />
        </div>
        <span className="metric-hint">AI neural synthesizer traces</span>
      </div>

      {snr !== null && (
        <div className="metric-card">
          <div className="metric-header">
            <span>Signal-to-Noise (SNR)</span>
            <strong className={snr >= 20 ? "text-safe" : snr >= 10 ? "text-warning" : "text-danger"}>
              {snr.toFixed(1)} dB
            </strong>
          </div>
          <div className="metric-bar-track">
            <div
              className={`metric-bar-fill ${snr >= 20 ? "fill-safe" : snr >= 10 ? "fill-warning" : "fill-danger"}`}
              style={{ width: `${Math.max(5, Math.min(100, (snr / 40) * 100))}%` }}
            />
          </div>
          <span className="metric-hint">Acoustic recording clarity & clean floor</span>
        </div>
      )}
    </div>
  );
}
