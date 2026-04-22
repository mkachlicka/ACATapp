import sys
from pathlib import Path

_SUPPORT_PATH = Path(__file__).parent / "support"
_SUPPORT_FUNC_PATH = _SUPPORT_PATH / "functions"
_BIN_PATH = _SUPPORT_PATH / ".." / ".." / ".." / ".." / "bin"


def get_praat_func_dir() -> Path:
    try:
        return Path(sys._MEIPASS) / "praat"
    except AttributeError:
        return _SUPPORT_FUNC_PATH


def get_ffmpeg_path_dir() -> Path | None:
    try:
        bin_path = Path(sys._MEIPASS) / "bin"
        if sys.platform == "darwin" or sys.platform == "linux":
            ffmpeg_path = bin_path / "ffmpeg"
        elif sys.platform == "win32":
            ffmpeg_path = bin_path / "ffmpeg.exe"
        else:
            raise NotImplementedError(f"Unsupported platform: {sys.platform}")

        return ffmpeg_path.absolute()

    except AttributeError as e:
        return None


def bind_ffmpeg() -> None:
    from pydub import AudioSegment

    if ffmpeg_path := get_ffmpeg_path_dir():
        AudioSegment.converter = str(ffmpeg_path)
