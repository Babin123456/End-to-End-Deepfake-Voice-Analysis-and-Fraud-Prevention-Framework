from fastapi import APIRouter, File, HTTPException, UploadFile

try:
    from schemas.batch import BatchAnalysisResponse
    from services.batch_analyzer import analyze_audio_batch
except ImportError:
    from backend.schemas.batch import BatchAnalysisResponse
    from backend.services.batch_analyzer import analyze_audio_batch

router = APIRouter(prefix="/analyze/batch", tags=["Batch Voice Analysis"])

MAX_BATCH_FILES = 50


@router.post("", response_model=BatchAnalysisResponse)
async def analyze_batch(files: list[UploadFile] = File(...)):
    """
    Process multiple voice audio recordings in a single batch request
    and compile aggregate campaign threat intelligence.
    """
    if not files:
        raise HTTPException(
            status_code=400,
            detail="No audio files provided. Please upload at least one audio sample.",
        )

    if len(files) > MAX_BATCH_FILES:
        raise HTTPException(
            status_code=400,
            detail=f"Batch size exceeds maximum limit of {MAX_BATCH_FILES} files.",
        )

    file_items: list[tuple[str, bytes]] = []
    for f in files:
        filename = f.filename or "unnamed_audio.wav"
        contents = await f.read()
        file_items.append((filename, contents))

    return analyze_audio_batch(file_items)
