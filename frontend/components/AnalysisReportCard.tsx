"use client";

import React from "react";
import AudioPlayer from "./AudioPlayer";
import ForensicMetricsGrid from "./ForensicMetricsGrid";
import FraudAdvisoryPanel from "./FraudAdvisoryPanel";
import ForensicIndicatorList from "./ForensicIndicatorList";

type ForensicBreakdownType = {
  spectral_consistency?: number;
  pitch_naturalness?: number;
  vocoder_artifact_score?: number;
};

type FraudAdvisoryType = {
  sha256_hash?: string;
  impersonation_threat_score?: number;
  threat_category?: string;
  requires_human_escalation?: boolean;
  advisory_actions?: {
    action_type: string;
    description: string;
    severity: string;
  }[];
};

interface AnalysisReportCardProps {
  result: {
    filename?: string;
    status?: string;
    fake_probability?: number;
    confidence_score?: number;
    risk_level?: string;
    indicators?: string[];
    breakdown?: ForensicBreakdownType;
    fraud_prevention?: FraudAdvisoryType;
    sha256_hash?: string;
    [key: string]: unknown;
  } | null;
  loading: boolean;
  file?: File | null;
  onExport?: () => void;
}

export default function AnalysisReportCard({
  result,
  loading,
  file,
  onExport,
}: AnalysisReportCardProps) {
  const probability =
    result && typeof result.fake_probability === "number"
      ? result.fake_probability
      : null;

  return (
    <aside className="result-card" aria-live="polite">
      <div className="card-heading">
        <div>
          <p className="step-label">
            02 <span>/ RESULTS</span>
          </p>
          <h2>Analysis report</h2>
        </div>
        {result && (
          <span className="result-status">{result.status || "Complete"}</span>
        )}
      </div>

      {!result && !loading && (
        <div className="empty-result">
          <div className="report-graphic" aria-hidden="true">
            <span>〰</span>
            <span>〰</span>
            <span>〰</span>
          </div>
          <strong>Your report will appear here</strong>
          <p>Choose or record a WAV sample to inspect its forensic authenticity metrics.</p>
        </div>
      )}

      {loading && (
        <div className="empty-result">
          <div className="loading-graphic">
            <span />
            <span />
            <span />
            <span />
            <span />
          </div>
          <strong>Listening for signals…</strong>
          <p>Audio waveform is being evaluated by the detection model.</p>
        </div>
      )}

      {result && !loading && (
        <div className="report-content">
          <div className="report-file">
            <span className="mini-audio">♫</span>
            <div>
              <strong>{result.filename || file?.name || "Audio file"}</strong>
              <span>Server response received</span>
            </div>
            {onExport && (
              <button
                type="button"
                className="export-trigger-btn"
                onClick={onExport}
                aria-label="Export forensic report"
              >
                Export Case ↓
              </button>
            )}
          </div>

          {/* Integrated Audio Playback & Waveform Preview */}
          {file && (
            <div className="report-audio-player-wrapper">
              <AudioPlayer file={file} />
            </div>
          )}

          {probability !== null ? (
            <div className="probability-block">
              <div className="probability-top">
                <span>Fake voice probability</span>
                <strong>{(probability * 100).toFixed(1)}%</strong>
              </div>
              <div className="probability-track">
                <span
                  style={{
                    width: `${Math.max(0, Math.min(100, probability * 100))}%`,
                  }}
                />
              </div>
            </div>
          ) : (
            <div className="response-note">
              <strong>Analysis status</strong>
              <span>{result.status || "The API returned a result."}</span>
            </div>
          )}

          <ForensicMetricsGrid breakdown={result.breakdown} />

          <ForensicIndicatorList
            indicators={result.indicators}
            riskLevel={result.risk_level}
          />

          <FraudAdvisoryPanel
            fraudData={result.fraud_prevention}
            fakeProbability={result.fake_probability}
          />

          <details className="raw-response">
            <summary>View full API response</summary>
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </details>
        </div>
      )}

      <div className="result-footnote">
        <span className="info-mark">i</span> Results depend on the analysis
        model and should not be treated as definitive proof.
      </div>
    </aside>
  );
}
