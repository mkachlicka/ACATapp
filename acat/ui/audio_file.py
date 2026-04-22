from __future__ import annotations

import pathlib
from dataclasses import dataclass, field
from typing import Iterable

import parselmouth


@dataclass
class PraatScore:
    """Scores generated from Praat analysis that will be displayed and export as CSV"""

    comprehensibility: float
    nativelikeness: float
    speechrate: float
    pauses: float
    rangef0: float
    sdsylldur: float
    coeff1: float
    coeff2: float
    coeff3: float

    @property
    def all_data(self) -> Iterable[float]:
        return [
            self.comprehensibility,
            self.nativelikeness,
            self.speechrate,
            self.pauses,
            self.rangef0,
            self.sdsylldur,
            self.coeff1,
            self.coeff2,
            self.coeff3,
        ]

    @staticmethod
    def all_data_or_none(obj: PraatScore | None) -> Iterable[float | None]:
        if obj is None:
            return [None for _ in range(9)]
        return obj.all_data


@dataclass
class AudioFileInfo:
    path: pathlib.Path
    score: PraatScore | None = field(default=None)
    _duration: float = field(default=0.0, init=False, repr=False)

    def __post_init__(self) -> None:
        sound = parselmouth.Sound(str(self.path))
        self._duration = sound.duration

    @property
    def extension(self) -> str:
        return self.path.suffix

    @property
    def file_name(self) -> str:
        return self.path.name

    @property
    def audio_length(self) -> float:
        return self._duration

    @property
    def audio_length_str(self) -> str:
        return f"{self.audio_length:.2f} s"

    @property
    def comprehensibility(self) -> float | None:
        if self.score:
            return self.score.comprehensibility
        return None

    @property
    def nativelikeness(self) -> float | None:
        if self.score:
            return self.score.nativelikeness
        return None

    @property
    def comprehensibility_str(self) -> str:
        if self.comprehensibility:
            return f"{self.comprehensibility:.5f}"
        return "N/A"

    @property
    def nativelikeness_str(self) -> str:
        if self.nativelikeness:
            return f"{self.nativelikeness:.5f}"
        return "N/A"

    @property
    def formatted_score(self) -> str:
        return f"{self.comprehensibility_str} | {self.nativelikeness_str}"
