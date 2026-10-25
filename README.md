# 🎙️ End-to-End Deepfake Voice Analysis Framework

![NSoC 2026](https://img.shields.io/badge/NSoC-2026-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10+-yellow.svg)
![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)
![Tests](https://img.shields.io/badge/Tests-Pytest-brightgreen.svg)

An open-source ecosystem designed to detect synthetic audio and prevent voice-cloning fraud. This project combines a modern web dashboard with an AI-driven machine learning backend to analyze audio files for deepfake signatures.

---

## ✨ Features

- **Multi-Heuristic Forensic Synthetic Voice Detection Engine**:
  - **Pitch Jitter Analysis**: Measures vocal micro-perturbations to identify robotic pitch constancy (typical in text-to-speech synthesis) or unnatural frequency fluctuations.
  - **Amplitude Shimmer Evaluation**: Detects suppression of biological respiratory tremors and micro-variations.
  - **Neural Vocoder Artifact Detection**: Scans frequency spectra for high-frequency cliff cutoffs, phase discontinuities, and artificial dynamic range compression commonly introduced by neural vocoders (e.g., HiFi-GAN, WaveGrad).
  - **Acoustic Profiling**: Extracts zero-crossing rate (ZCR), root-mean-square (RMS) energy, spectral centroid, spectral rolloff, spectral flatness, and fundamental frequency ($f_0$).
- **Fraud Prevention & Risk Mitigation Engine**:
  - **Impersonation Threat Scoring**: Classifies uploaded samples into distinct threat levels (`AUTHENTIC_HUMAN_SPEECH`, `SUSPECTED_VOICE_SYNTHESIS`, or `CRITICAL_VOICE_CLONING_FRAUD`).
  - **Automated Advisory Actions**: Prescribes real-time operational countermeasures such as step-up multi-factor challenges (MFA), callback verifications, and voice biometric token revocations.
  - **Cryptographic Audio Fingerprinting**: Generates SHA-256 digests for tamper evidence and verification.
  - **Structured Incident Audit Logging**: Records security events with unique identifiers (`INC-XXXXXXXXXXXX`) into a persistent JSONL audit log (`fraud_audit_events.log`).
- **Robust Audio Validation & Preprocessing**:
  - Enforces canonical RIFF/WAVE stream validation, sample rate integrity, and audio duration limits (0.25s minimum to 300s maximum).
  - Normalizes audio data and downmixes multi-channel stereo audio to mono float32.
  - Protects the server against memory exhaustion via streaming upload size limit middleware (`UploadSizeLimitMiddleware`).
- **Environment-Based Configurations**:
  - Centralized, cached settings powered by `core/config.py` with support for local `.env` files.
  - Easily customize host, port, allowed CORS origins, and upload payload boundaries.
- **API Health Checks**:
  - Dedicated `/api/v1/health` monitoring route providing system status, server uptime, runtime platform, Python version, and active upload boundaries.
- **Modern Interactive Web Dashboard**:
  - Clean Next.js 14 and Tailwind CSS user interface with drag-and-drop WAV audio upload.
  - Integrated audio player with playback controls, seeking scrubber, and interactive waveform visualizer.
  - Comprehensive forensic report display showing fake probability scores, risk badges, and raw JSON response data.
- **Automated Pytest Suite**:
  - Comprehensive backend unit and integration test suite testing API routes, health checks, upload validations, and environment configurations.

---

## 🏗️ Architecture

This is a monorepo consisting of:
*   **Frontend:** A Next.js web application allowing users to upload audio files, preview recordings with waveform visualizations, and inspect detailed forensic reports.
*   **Backend:** A Python FastAPI server handling API requests, file validation, forensic feature extraction, and fraud prevention evaluations.
*   **Model & Forensic Engine:** Scientific audio processing services using NumPy and SciPy to extract acoustic parameters, evaluate vocoder anomalies, and calculate synthetic voice likelihood.

---

## ⚙️ How It Works

```
[ User Upload (.wav) ]
          │
          ▼
[ Next.js Frontend Dashboard ]
   ├─ Interactive Audio Player Preview
   └─ Real-Time Waveform Visualizer
          │ (POST /api/v1/analyze)
          ▼
[ FastAPI Backend Gateway ]
   ├─ UploadSizeLimitMiddleware (Max 25 MB)
   ├─ RIFF/WAVE Header & Duration Validation
   └─ SHA-256 Audio Fingerprint Computation
          │
          ▼
[ Acoustic Feature Extraction ]
   ├─ Time-Domain Analysis (Zero-Crossing Rate, RMS Energy)
   ├─ Frequency-Domain STFT (Spectral Centroid, Rolloff, Flatness)
   └─ Pitch Perturbation Estimation (F0, Pitch Jitter, Amplitude Shimmer)
          │
          ▼
[ Forensic Synthetic Voice Engine ]
   ├─ Pitch Jitter Micro-Perturbation Scoring
   ├─ Respiratory Shimmer Micro-Tremor Check
   ├─ Neural Vocoder Artifact Detection (Spectral Cliff & Phase Discontinuities)
   └─ Aggregate Fake Probability Calculation & Confidence Rating
          │
          ▼
[ Fraud Prevention Engine & Audit Logger ]
   ├─ Impersonation Threat Categorization
   ├─ Advisory Mitigation Actions (MFA, Callback, Biometric Revocation)
   └─ Persistent Structured JSONL Incident Log (fraud_audit_events.log)
          │
          ▼
[ JSON Response Rendered on Dashboard ]
```

1. **Upload & Preview**: The user uploads a `.wav` recording through the web dashboard. The browser renders an interactive player with playback controls and a waveform visualizer.
2. **Validation & Hashing**: The file is streamed to `POST /api/v1/analyze`. The backend verifies the RIFF/WAVE header, checks duration boundaries (0.25s - 300s), downmixes channels to mono float32, and computes an immutable SHA-256 fingerprint.
3. **Feature Extraction**: STFT and signal analysis compute zero-crossing rates, RMS energy, spectral rolloff, spectral flatness, fundamental frequency, pitch jitter, and amplitude shimmer.
4. **Forensic Detection**: The multi-heuristic engine checks whether vocal micro-perturbations fall outside natural human ranges or exhibit neural vocoder artifacts.
5. **Fraud Risk & Audit**: The fraud prevention engine assigns an impersonation threat score and generates security advisories. An audit incident (`INC-...`) is logged to disk.
6. **Report Delivery**: The frontend displays the fake voice probability bar, risk tier, forensic breakdown, and full diagnostic details.

---

## 📁 Project Structure

```
End-to-End-Deepfake-Voice-Analysis-and-Fraud-Prevention-Framework/
├── backend/
│   ├── api/
│   │   └── v1/
│   │       ├── health.py              # Health check endpoint router
│   │       └── __init__.py
│   ├── core/
│   │   ├── config.py                 # Environment settings & configuration loader
│   │   ├── constants.py              # Forensic thresholds & risk scoring constants
│   │   ├── security.py               # Cryptographic SHA-256 hashing utility
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── audio.py                  # Pydantic models for acoustic features
│   │   ├── detection.py              # Pydantic models for forensic detection results
│   │   ├── fraud.py                  # Pydantic models for fraud reports & audit logs
│   │   └── __init__.py
│   ├── services/
│   │   ├── audio_validator.py        # WAV stream validation, decoding & normalization
│   │   ├── audit_logger.py           # Structured JSONL incident logging
│   │   ├── detector.py               # Multi-heuristic forensic synthetic voice detector
│   │   ├── feature_extractor.py      # Acoustic feature extraction (STFT, jitter, shimmer)
│   │   ├── fraud_engine.py           # Fraud risk evaluation & advisory countermeasures
│   │   ├── vocoder_analyzer.py       # Neural vocoder artifact analysis
│   │   └── __init__.py
│   ├── tests/
│   │   ├── conftest.py               # Pytest fixtures and mock audio generators
│   │   ├── test_api_endpoints.py     # End-to-end tests for analysis & file validation
│   │   └── test_health_config.py     # Tests for health checks and environment configs
│   ├── .env.example                  # Template for backend environment variables
│   ├── .gitignore                    # Backend gitignore rules
│   ├── main.py                       # FastAPI entry point & middleware configuration
│   ├── pytest.ini                    # Pytest test runner settings
│   └── requirements.txt              # Python backend dependencies
├── frontend/
│   ├── app/
│   │   ├── globals.css               # Global styling and dashboard theme
│   │   ├── layout.tsx                # Next.js root layout
│   │   └── page.tsx                  # Main analysis dashboard view
│   ├── components/
│   │   ├── AnalysisReport.tsx        # Forensic results presentation card
│   │   ├── AudioPlayer.tsx           # Audio player with progress bar & playback controls
│   │   ├── AudioUpload.tsx           # Drag-and-drop file upload dropzone
│   │   ├── Navbar.tsx                # Application header navigation
│   │   └── WaveformVisualizer.tsx    # Waveform canvas preview
│   ├── hooks/
│   │   └── useAudioVisualizer.ts     # Audio playback state and Web Audio API hook
│   ├── public/                       # Static branding and icon assets
│   ├── types/
│   │   └── analysis.ts               # TypeScript interfaces for API responses
│   ├── package.json                  # Next.js, React, and Tailwind dependencies
│   ├── tsconfig.json                 # TypeScript compiler configuration
│   └── README.md                     # Frontend-specific documentation
├── CONTRIBUTING.md                   # NSoC 2026 contribution guidelines & code of conduct
├── LICENSE                           # Apache License 2.0
└── README.md                         # Main repository documentation
```

---

## 🔌 API Endpoints

The FastAPI backend exposes the following RESTful routes:

| Method | Endpoint | Description | Request Payload | Response Status & Body |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | Root service discovery | None | `200 OK`<br>`{ "message": "...", "version": "1.0.0", "service": "..." }` |
| `GET` | `/api/v1/health` | Health check & system diagnostics | None | `200 OK`<br>`{ "status": "ok", "uptime_seconds": ..., "python_version": "...", "upload_limits": { ... } }` |
| `POST` | `/api/v1/analyze` | Upload and analyze a WAV audio sample | `multipart/form-data`<br>`file: <audio.wav>` | `200 OK`<br>`{ "filename": "...", "status": "completed", "fake_probability": ..., "fraud_prevention": { ... }, "incident_id": "...", "sha256_hash": "..." }` |

### Error Responses

- **`400 Bad Request`**: Uploaded file is empty, missing a valid RIFF/WAVE header, uses an unsupported format (non-WAV), or fails duration bounds (<0.25s or >300s).
- **`413 Payload Too Large`**: Uploaded file size exceeds the configured `MAX_UPLOAD_SIZE` (default: 25 MB).
- **`422 Unprocessable Entity`**: Request body is missing the required `file` multipart field.

---

## 🚀 Quick Start (Local Setup)

### Prerequisites

Ensure you have the following installed on your machine:
- **Python**: Version 3.10 or higher
- **Node.js**: Version 18.x or higher
- **npm** / **yarn** / **pnpm**
- **Git**

---

### 1. Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   - **Linux / macOS**:
     ```bash
     python -m venv venv
     source venv/bin/activate
     ```
   - **Windows**:
     ```powershell
     python -m venv venv
     venv\Scripts\activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Copy the example environment configuration to create your local `.env` file:
   - **Linux / macOS**:
     ```bash
     cp .env.example .env
     ```
   - **Windows (Command Prompt / PowerShell)**:
     ```powershell
     copy .env.example .env
     ```
   *(Optional)* Open `.env` in your text editor and adjust configuration values as needed:
   ```dotenv
   HOST=127.0.0.1
   PORT=8000
   CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   MAX_UPLOAD_SIZE=26214400  # 25 MB in bytes
   UPLOAD_CHUNK_SIZE=1048576  # 1 MB in bytes
   ```

5. **Start the FastAPI server**:
   ```bash
   uvicorn main:app --reload
   ```
   The backend API will run at `http://localhost:8000`. You can test the health check route by visiting `http://localhost:8000/api/v1/health` or view the interactive OpenAPI documentation at `http://localhost:8000/docs`.

---

### 2. Frontend Setup

1. **Navigate to the frontend directory** (in a separate terminal window):
   ```bash
   cd frontend
   ```

2. **Install frontend dependencies**:
   ```bash
   npm install
   ```

3. **Start the Next.js development server**:
   ```bash
   npm run dev
   ```
   The dashboard UI will run at `http://localhost:3000`. Open your browser and navigate to `http://localhost:3000` to begin analyzing audio files.

---

### 3. Running Tests

The backend includes an automated test suite powered by `pytest` to verify API routes, health checks, upload limits, and file validation logic.

To run the test suite:

```bash
cd backend
python -m pytest tests
```

To run tests with detailed output:

```bash
cd backend
python -m pytest tests -v
```

---

## 🤝 Contributing

We welcome contributions for the **Nexus Spring of Code (NSoC) 2026**! 

> ⚠️ **Important NSoC 2026 Rule:** Do **NOT** submit a Pull Request without first creating or claiming an Issue and waiting to be officially assigned by [`@vanshi18s`](https://github.com/vanshi18s). Unassigned PRs will be closed per official NSoC guidelines.

1. Browse open tasks in the **Issues** tab or propose a new valid issue.
2. Comment on the issue to request assignment and wait for confirmation from `@vanshi18s`.
3. Read our [CONTRIBUTING.md](./CONTRIBUTING.md) guide before opening a Pull Request.

---

## 📄 License

This project is licensed under the Apache License 2.0. See the [LICENSE](./LICENSE) file for details.
