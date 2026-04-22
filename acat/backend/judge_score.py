import enum
import pathlib

from acat.backend.praat_score_judging_japanese import generate_praat_score_japanese_impl
from acat.ui.audio_file import PraatScore


class LanguageModel(enum.Enum):
    Japanese = "Japanese"


def generate_praat_score(
    audio_file_path: pathlib.Path, model: LanguageModel
) -> PraatScore:
    if model == LanguageModel.Japanese:
        return generate_praat_score_japanese_impl(audio_file_path)
    else:
        raise ValueError("Unknown Language Model")
