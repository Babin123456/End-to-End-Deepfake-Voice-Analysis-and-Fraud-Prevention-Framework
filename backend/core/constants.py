"""Forensic thresholds and detection constants for synthetic voice analysis."""

# Natural human voice normative ranges
HUMAN_MIN_PITCH_HZ = 70.0
HUMAN_MAX_PITCH_HZ = 500.0
HUMAN_MIN_JITTER = 0.005  # Below 0.5% indicates unnatural pitch perfection (TTS/cloning)
HUMAN_MAX_JITTER = 0.040  # Above 4.0% indicates unnatural jitter instability
HUMAN_MIN_SHIMMER = 0.015 # Below 1.5% indicates robotic amplitude constancy

# Risk level boundaries
RISK_THRESHOLD_LOW = 0.35
RISK_THRESHOLD_HIGH = 0.65

# Heuristic weights for fake probability calculation
WEIGHT_PITCH_PERFECTION = 0.30
WEIGHT_SHIMMER_ANOMALY = 0.20
WEIGHT_VOCODER_ARTIFACTS = 0.35
WEIGHT_SPECTRAL_INCOHERENCE = 0.15

# Forensic risk labels
RISK_LEVEL_LOW = "LOW_RISK"
RISK_LEVEL_SUSPICIOUS = "SUSPICIOUS"
RISK_LEVEL_HIGH = "HIGH_RISK_DEEPFAKE"

# Audio format and container definitions
SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".wave", ".mp3", ".ogg", ".flac", ".m4a", ".aac"}
MIME_TYPE_MAPPING = {
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "ogg": "audio/ogg",
    "flac": "audio/flac",
    "m4a": "audio/mp4",
}

