from pathlib import Path
import json
import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Deepfake Audio Detection API")

frontend_origin = os.getenv("FRONTEND_ORIGIN")
allowed_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
if frontend_origin:
    allowed_origins.append(frontend_origin.rstrip("/"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)

SUPPORTED_EXTENSIONS = {".wav", ".wave"}
MAX_UPLOAD_SIZE = 25 * 1024 * 1024
UPLOAD_CHUNK_SIZE = 1024 * 1024
UPLOAD_TOO_LARGE_DETAIL = "Upload is too large. Maximum request size is 25 MB."


class UploadSizeLimitMiddleware:
    """Limit the streamed request body for the audio-analysis endpoint."""

    def __init__(self, app, max_bytes: int = MAX_UPLOAD_SIZE):
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope, receive, send):
        if (
            scope["type"] != "http"
            or scope.get("method") != "POST"
            or scope.get("path") != "/api/v1/analyze"
        ):
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        content_length = headers.get(b"content-length")
        if content_length is not None:
            try:
                declared_length = int(content_length)
            except ValueError:
                await self._respond(send, 400, "Invalid Content-Length header.")
                return
            if declared_length < 0:
                await self._respond(send, 400, "Invalid Content-Length header.")
                return
            if declared_length > self.max_bytes:
                await self._respond(send, 413, UPLOAD_TOO_LARGE_DETAIL)
                return

        received = 0
        too_large = False

        async def limited_receive():
            nonlocal received, too_large
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    too_large = True
                    raise _UploadTooLarge
            return message

        async def guarded_send(message):
            # Starlette may try to emit an error response after limited_receive
            # raises. The middleware owns the 413 response in that case.
            if not too_large:
                await send(message)

        try:
            await self.app(scope, limited_receive, guarded_send)
        except _UploadTooLarge:
            await self._respond(send, 413, UPLOAD_TOO_LARGE_DETAIL)

    @staticmethod
    async def _respond(send, status_code: int, detail: str):
        body = json.dumps({"detail": detail}).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": status_code,
            "headers": [
                (b"content-type", b"application/json"),
                (b"content-length", str(len(body)).encode("ascii")),
            ],
        })
        await send({"type": "http.response.body", "body": body})

class _UploadTooLarge(Exception):
    """Internal signal used to stop reading an oversized request."""


app.add_middleware(UploadSizeLimitMiddleware)


import sys

backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    from services.audio_validator import validate_and_decode_wav
    from services.feature_extractor import extract_acoustic_features
    from services.detector import detect_synthetic_voice
except ImportError:
    from backend.services.audio_validator import validate_and_decode_wav
    from backend.services.feature_extractor import extract_acoustic_features
    from backend.services.detector import detect_synthetic_voice


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Deepfake Audio Detection API",
        "version": "1.0.0",
        "service": "deepfake-voice-analysis-engine",
    }


@app.post("/api/v1/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    filename = file.filename or "audio_sample.wav"
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported audio format. Please upload a .wav or .wave file.",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded audio file is empty.",
        )

    # Decode and validate audio stream
    audio, sample_rate, channels = validate_and_decode_wav(contents)

    # Extract forensic acoustic features
    features = extract_acoustic_features(audio, sample_rate=sample_rate, channels=channels)

    # Run multi-heuristic deepfake detection engine
    detection = detect_synthetic_voice(
        audio=audio,
        sample_rate=sample_rate,
        pitch_jitter=features.pitch_jitter,
        shimmer=features.shimmer,
        spectral_flatness=features.spectral_flatness,
    )

    return {
        "filename": filename,
        "status": "completed",
        "fake_probability": detection.fake_probability,
        "confidence_score": detection.confidence_score,
        "risk_level": detection.risk_level,
        "indicators": detection.indicators,
        "features": features.model_dump(),
        "breakdown": detection.breakdown.model_dump(),
    }

