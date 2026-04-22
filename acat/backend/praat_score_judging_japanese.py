import io
import pathlib
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd
import parselmouth
from praatio import textgrid

from acat.backend.utils import get_praat_func_dir
from acat.ui.audio_file import PraatScore

_ANALYSIS_PRAAT_SCRIPT = get_praat_func_dir() / "SyllableNucleiv3.praat"
_ANALYSIS_PRAAT_SCRIPT_STR = str(_ANALYSIS_PRAAT_SCRIPT.absolute())

with open(_ANALYSIS_PRAAT_SCRIPT_STR, "rb") as f:
    f.read()


def _generate_file_spec(audio_file_path: Path) -> str:
    # TODO: change this to a more restrictive file spec
    return f"{str(audio_file_path.absolute())}*"


def _get_text_grid_path(audio_file_path: Path) -> Path:
    return audio_file_path.absolute().with_suffix(".auto.TextGrid")


def _run_praat_script(audio_file_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    audio_file_path_str = _generate_file_spec(audio_file_path)
    tab1 = parselmouth.praat.run_file(
        _ANALYSIS_PRAAT_SCRIPT_STR,
        audio_file_path_str,
        "None",
        -25,
        2,
        0.4,
        True,
        "English",
        1,
        "Table",
        "OverWriteData",
        True,
    )

    tab2 = parselmouth.praat.run_file(
        _ANALYSIS_PRAAT_SCRIPT_STR,
        audio_file_path_str,
        "None",
        -25,
        2,
        0.4,
        True,
        "English",
        1,
        "Table",
        "OverWriteData",
        False,
    )

    return pd.read_table(
        io.StringIO(parselmouth.praat.call(tab1[2], "List", False))
    ), pd.read_table(io.StringIO(parselmouth.praat.call(tab2[0], "List", False)))


def _analysis_from_praat_script(
    audio_file_path: Path,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    true_data, false_data = _run_praat_script(audio_file_path)

    selected_cols = ["type", "F0", "F1", "F2", "F3"]
    true_data = true_data[selected_cols]

    # TODO: this is a temporary fix. To be confirmed this is the right way to do it.
    true_data = true_data[true_data["type"] == "?"]  # syll are labeled as ?

    true_data.replace("--undefined--", np.nan, inplace=True)
    true_data = true_data.astype({"F0": float, "F1": float, "F2": float, "F3": float})

    true_data_sub = pd.DataFrame(
        {
            "meanf0": true_data["F0"].mean(skipna=True),
            "meanf1": true_data["F1"].mean(skipna=True),
            "meanf2": true_data["F2"].mean(skipna=True),
            "meanf3": true_data["F3"].mean(skipna=True),
            "sdf0": true_data["F0"].std(skipna=True),
            "sdf1": true_data["F1"].std(skipna=True),
            "sdf2": true_data["F2"].std(skipna=True),
            "sdf3": true_data["F3"].std(skipna=True),
            "minf0": true_data["F0"].min(skipna=True),
            "maxf0": true_data["F0"].max(skipna=True),
        },
        index=[0],
    )

    true_data_sub["rangef0"] = true_data_sub["maxf0"] - true_data_sub["minf0"]
    true_data_sub["coeff1"] = np.log10(true_data_sub["sdf1"] / true_data_sub["meanf1"])
    true_data_sub["coeff2"] = np.log10(true_data_sub["sdf2"] / true_data_sub["meanf2"])
    true_data_sub["coeff3"] = np.log10(true_data_sub["sdf3"] / true_data_sub["meanf3"])
    true_data_sub = true_data_sub[["rangef0", "coeff1", "coeff2", "coeff3"]]

    false_data.columns = false_data.columns.str.strip()
    false_data = false_data.rename(columns={"speechrate(nsyll/dur)": "speechrate"})
    false_data["pauses"] = false_data["npause"] + false_data["nrFP"]
    false_data = false_data[["speechrate", "pauses"]]

    return true_data_sub, false_data


def _analyze_text_grid(text_grid_path: pathlib.Path) -> pd.DataFrame:
    text_grid_path_str = str(text_grid_path.absolute())

    # TODO: this is a temporary fix. To be confirmed this is the right way to do it.
    # syll are labeled as ""
    tg = textgrid.openTextgrid(text_grid_path_str, includeEmptyIntervals=True)

    tier = tg.getTier(tg.tierNames[2])

    start_times = []
    end_times = []
    labels = []

    for interval in tier.entries:
        start_times.append(interval[0])
        end_times.append(interval[1])
        labels.append(interval[2])

    textgrid_df = pd.DataFrame(
        np.column_stack(
            [start_times, end_times, labels, np.subtract(end_times, start_times)]
        ),
        columns=["start", "stop", "type", "diff"],
    )
    textgrid_df = textgrid_df.astype({"start": float, "stop": float, "diff": float})

    # TODO: this is a temporary fix. To be confirmed this is the right way to do it.
    textgrid_df = textgrid_df[
        (textgrid_df["type"] == "syll") | (textgrid_df["type"] == "")
    ]  # syll are labeled as ""
    textgrid_df.replace("--undefined--", np.nan, inplace=True)

    df_sub = pd.DataFrame(
        {"sdsylldur": np.log10(textgrid_df["diff"].std(skipna=True))}, index=[0]
    )

    return df_sub


def generate_praat_score_japanese_impl(audio_file_path: pathlib.Path) -> PraatScore:
    df1, df2 = _analysis_from_praat_script(audio_file_path)
    df3 = _analyze_text_grid(_get_text_grid_path(audio_file_path))
    final = pd.concat([df2, df3, df1], axis=1)

    comp_avg = (
        2.138
        + (2.701 * final["speechrate"])
        + (0.015 * final["pauses"])
        + (-0.020 * final["rangef0"])
        + (3.821 * final["sdsylldur"])
        + (-1.414 * final["coeff1"])
        + (-5.549 * final["coeff2"])
        + (3.228 * final["coeff3"])
    )
    comp_score = comp_avg.iloc[0]

    native_avg = (
        -0.537
        + (2.654 * final["speechrate"])
        + (-0.001 * final["pauses"])
        + (-0.019 * final["rangef0"])
        + (3.170 * final["sdsylldur"])
        + (-0.622 * final["coeff1"])
        + (-8.016 * final["coeff2"])
        + (3.575 * final["coeff3"])
    )
    native_score = native_avg.iloc[0]

    partial_data = map(
        lambda x: x[0],
        [
            final["speechrate"],
            final["pauses"],
            final["rangef0"],
            final["sdsylldur"],
            final["coeff1"],
            final["coeff2"],
            final["coeff3"],
        ],
    )

    return PraatScore(
        comp_score,
        native_score,
        *partial_data,
    )
