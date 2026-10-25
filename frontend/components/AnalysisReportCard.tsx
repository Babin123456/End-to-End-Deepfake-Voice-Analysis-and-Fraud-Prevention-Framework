"use client";

import React from "react";
import { AnalysisResult } from "../types/analysis";

interface AnalysisReportCardProps {
  result: AnalysisResult | null;
  loading: boolean;
  selectedFileName?: string;
}

export default function AnalysisReportCard({
  result,
  loading,
  selectedFileName,
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
          <p>
            Choose a WAV file and run the analysis to see the response from the
            detection API.
          </p>
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
          <p>Your audio is being sent to the backend for analysis.</p>
        </div>
      )}

      {result && !loading && (
        <div className="report-content">
          <div className="report-file">
            <span className="mini-audio">♫</span>
            <div>
              <strong>{result.filename || selectedFileName || "Audio file"}</strong>
              <span>Server response received</span>
            </div>
          </div>

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
