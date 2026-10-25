from typing import Optional
from pydantic import BaseModel, Field


class AcousticFeatures(BaseModel):
    sample_rate: int = Field(..., description="Sampling rate in Hz")
    duration_seconds: float = Field(..., description="Duration of audio in seconds")
    channels: int = Field(..., description="Number of audio channels (1 for mono, 2 for stereo)")
    zero_crossing_rate: float = Field(..., description="Mean zero-crossing rate of the audio signal")
    rms_energy: float = Field(..., description="Root-mean-square energy indicating loudness dynamics")
    spectral_centroid_hz: float = Field(..., description="Center of mass of the frequency spectrum in Hz")
    spectral_rolloff_hz: float = Field(..., description="Frequency below which 85% of spectral energy lies")
    spectral_flatness: float = Field(..., description="Measure of noisiness versus tonality (0 to 1)")
    fundamental_frequency_hz: Optional[float] = Field(None, description="Estimated average pitch (F0) in Hz")
    pitch_jitter: Optional[float] = Field(None, description="Cycle-to-cycle pitch period variation")
    shimmer: Optional[float] = Field(None, description="Cycle-to-cycle amplitude perturbation")
