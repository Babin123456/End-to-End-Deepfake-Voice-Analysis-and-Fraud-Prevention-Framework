"use client";

import { useState } from "react";
import Navbar from "../components/Navbar";
import AudioUploadCard from "../components/AudioUploadCard";
import AnalysisReportCard from "../components/AnalysisReportCard";
import { AnalysisResult } from "../types/analysis";

const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [currentFileName, setCurrentFileName] = useState<string>("");

  async function handleAnalyze(file: File) {
    setLoading(true);
    setError("");
    setResult(null);
    setCurrentFileName(file.name);

    const body = new FormData();
    body.append("file", file);

    try {
      const response = await fetch(`${API_URL}/api/v1/analyze`, {
        method: "POST",
        body,
      });

      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        const detail = payload && typeof payload.detail === "string" ? payload.detail : "";
        throw new Error(detail || `Analysis failed (HTTP ${response.status}).`);
      }

      if (!payload || typeof payload !== "object") {
        throw new Error("The server returned an unexpected response.");
      }

      setResult(payload as AnalysisResult);
    } catch (caught) {
      setError(
        caught instanceof TypeError
          ? `Could not connect to the analysis API at ${API_URL}. Make sure the backend is running and CORS is configured.`
          : caught instanceof Error
            ? caught.message
            : "Something went wrong while analyzing the audio.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="analysis-shell">
      <Navbar />

      <section className="hero">
        <p className="eyebrow">DEEPFAKE VOICE DETECTION</p>
        <h1>
          Is this voice <span>really real?</span>
        </h1>
        <p className="hero-copy">
          Upload an audio recording to check it for signs of synthetic or manipulated speech.
        </p>
      </section>

      <section className="workspace" aria-label="Audio analysis">
        <AudioUploadCard
          onAnalyze={handleAnalyze}
          loading={loading}
          error={error}
        />

        <AnalysisReportCard
          result={result}
          loading={loading}
          selectedFileName={currentFileName}
        />
      </section>

      <footer className="page-footer">
        <span>VOXSHIELD · AUDIO FORENSICS</span>
        <span>Supported format: WAV / WAVE</span>
      </footer>
    </main>
  );
}
