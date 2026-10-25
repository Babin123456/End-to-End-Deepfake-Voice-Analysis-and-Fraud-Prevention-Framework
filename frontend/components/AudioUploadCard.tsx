"use client";

import React, { ChangeEvent, DragEvent, FormEvent, useRef, useState } from "react";

interface AudioUploadCardProps {
  onAnalyze: (file: File) => Promise<void>;
  loading: boolean;
  error: string;
}

const MAX_FILE_BYTES = 25 * 1024 * 1024; // 25 MB

function formatBytes(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function AudioUploadCard({ onAnalyze, loading, error }: AudioUploadCardProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [validationError, setValidationError] = useState("");

  function selectFile(candidate?: File) {
    setValidationError("");
    if (!candidate) return;

    const extension = candidate.name.toLowerCase().slice(candidate.name.lastIndexOf("."));
    if (![".wav", ".wave"].includes(extension)) {
      setFile(null);
      setValidationError("Please choose a WAV audio file (.wav or .wave).");
      return;
    }

    if (candidate.size > MAX_FILE_BYTES) {
      setFile(null);
      setValidationError("This file is larger than 25 MB. Choose a smaller audio file.");
      return;
    }

    setFile(candidate);
  }

  function onInputChange(event: ChangeEvent<HTMLInputElement>) {
    selectFile(event.target.files?.[0]);
    event.target.value = "";
  }

  function onDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setDragging(false);
    selectFile(event.dataTransfer.files?.[0]);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file || loading) return;
    await onAnalyze(file);
  }

  const activeError = validationError || error;

  return (
    <form className="upload-card" onSubmit={handleSubmit}>
      <div className="card-heading">
        <div>
          <p className="step-label">
            01 <span>/ UPLOAD</span>
          </p>
          <h2>Choose an audio file</h2>
        </div>
        <span className="file-type">WAV · MAX 25 MB</span>
      </div>

      <div
        className={`dropzone ${dragging ? "dropzone-active" : ""} ${file ? "dropzone-selected" : ""}`}
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
      >
        <input
          ref={inputRef}
          className="visually-hidden"
          type="file"
          accept=".wav,.wave,audio/wav,audio/wave"
          onChange={onInputChange}
          aria-label="Choose WAV audio file"
        />
        {file ? (
          <>
            <div className="audio-icon selected-icon" aria-hidden="true">
              ♫
            </div>
            <div className="selected-file">
              <strong>{file.name}</strong>
              <span>{formatBytes(file.size)} · Ready to analyze</span>
            </div>
            <button
              className="change-file"
              type="button"
              onClick={() => inputRef.current?.click()}
            >
              Change
            </button>
          </>
        ) : (
          <>
            <div className="audio-icon" aria-hidden="true">
              ↑
            </div>
            <strong className="drop-title">Drop your audio file here</strong>
            <span className="drop-subtitle">or browse files from your device</span>
            <button
              className="browse-button"
              type="button"
              onClick={() => inputRef.current?.click()}
            >
              Browse files
            </button>
          </>
        )}
      </div>

      {activeError && (
        <p className="error-message" role="alert">
          <span aria-hidden="true">!</span>
          {activeError}
        </p>
      )}

      <div className="upload-footer">
        <p>
          <span className="lock-icon" aria-hidden="true">
            ◇
          </span>{" "}
          Audio is sent to your configured analysis server.
        </p>
        <button
          className="analyze-button"
          type="submit"
          disabled={!file || loading}
        >
          {loading ? (
            <>
              <span className="spinner" /> Analyzing audio…
            </>
          ) : (
            <>
              Analyze audio <span aria-hidden="true">→</span>
            </>
          )}
        </button>
      </div>
    </form>
  );
}
