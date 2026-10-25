export interface AcousticFeatures {
  sample_rate?: number;
  duration_seconds?: number;
  channels?: number;
  zero_crossing_rate?: number;
  rms_energy?: number;
  spectral_centroid_hz?: number;
  spectral_rolloff_hz?: number;
  spectral_flatness?: number;
  fundamental_frequency_hz?: number | null;
  pitch_jitter?: number | null;
  shimmer?: number | null;
}

export interface ForensicBreakdown {
  spectral_consistency?: number;
  pitch_naturalness?: number;
  vocoder_artifact_score?: number;
}

export interface AnalysisResult {
  filename: string;
  status: string;
  fake_probability: number;
  confidence_score?: number;
  risk_level?: "LOW_RISK" | "SUSPICIOUS" | "HIGH_RISK_DEEPFAKE";
  indicators?: string[];
  features?: AcousticFeatures;
  breakdown?: ForensicBreakdown;
  timestamp?: string;
  [key: string]: unknown;
}
