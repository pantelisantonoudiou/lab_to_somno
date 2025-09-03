# -*- coding: utf-8 -*-
"""
Convert LabChart comments (from ANY channel in the Excel group) to Visbrain hypnogram text files.

Workflow
--------
1) Convert LabChart .adicht files to EDF (separate script).
2) Use THIS script to convert LabChart comments -> Visbrain-format .txt hypnograms.
   - For each recording_id in the Excel:
       * Read the LabChart file once
       * Collect comments from ALL channels listed for that recording
       * Merge, sort by time, resolve duplicate timestamps, map to Somnotate labels
       * Write one .txt hypnogram file

Edit ONLY the USER SETTINGS block at the bottom.
"""

#### -------------------------- Imports -------------------------- ####
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import adi
#### ------------------------------------------------------------- ####


def comments_to_visbrain(com_df: pd.DataFrame, state_map: dict, add_initial_zero=True):
    """
    Convert a comment DataFrame to Visbrain hypnogram lines.

    Parameters
    ----------
    com_df : pd.DataFrame
        Must contain 'com_time' (float seconds) and 'com_text' (str labels).
        Rows should be for the relevant channels only (already filtered).
    state_map : dict[str, str]
        Map raw LabChart comment -> Somnotate label (e.g., "WAKE" -> "awake").
    add_initial_zero : bool
        If True, writes the first state at t=0.

    Returns
    -------
    list[str]
        Lines to write into a Visbrain hypnogram file, including *Duration_sec header.
        Returns [] if labels cannot be mapped.
    """

    if com_df.empty:
        return []

    # Sort and resolve duplicate timestamps:
    # - If multiple comments share the exact same 'com_time', keep the LAST one
    #   (this mirrors a "latest wins" approach; change to keep='first' if preferred).
    com_df = (
        com_df.sort_values(["com_time", "channel_id"])
              .drop_duplicates(subset=["com_time"], keep="last")
              .reset_index(drop=True)
    )

    # Map labels
    somno_labels = [state_map.get(txt, txt) for txt in com_df["com_text"].astype(str)]
    com_times = com_df["com_time"].astype(float).values

    # Validate mapped labels
    allowed = set(state_map.values()) | {"undefined"}
    unknown = set(somno_labels) - allowed
    if unknown:
        print(f"--> Unmapped/unknown labels encountered: {unknown}")
        return []

    lines = []
    # Duration: round up to nearest whole second
    file_duration = float(np.ceil(com_times[-1])) if len(com_times) else 0.0
    lines.append(f"*Duration_sec\t{file_duration}")
    lines.append("*Datafile\tUnspecified")

    if add_initial_zero and len(com_times) > 0:
        lines.append(f"{somno_labels[0]}\t0")

    # Subsequent transitions
    for label, t in zip(somno_labels[1:], com_times[1:]):
        lines.append(f"{label}\t{t}")

    if len(com_times) and file_duration > com_times[-1]:
        lines.append(f"undefined\t{file_duration}")

    return lines


def convert_annotations_any_channel(
    selected_recordings: pd.DataFrame,
    labchart_path: str,
    save_path: str,
    state_map: dict,
    animal_position_col: str = "animal_position",
    file_name_col: str = "file_name",
    channel_id_col: str = "channel_id",
):
    """
    Create one hypnogram per recording_id using comments from ALL channels listed in Excel.

    Parameters
    ----------
    selected_recordings : pd.DataFrame
        Must include: recording_id, file_name, channel_id, animal_position (+ any others you track).
        There should be multiple rows per recording_id (one per channel).
    labchart_path : str
        Folder containing the .adicht files.
    save_path : str
        Output folder for hypnogram .txt files (auto-created).
    state_map : dict[str, str]
        LabChart comment -> Somnotate label mapping.
    animal_position_col, file_name_col, channel_id_col : str
        Column names in your Excel for animal position, file name, and channel id respectively.
        channel_id is assumed 1-based in Excel and converted to 0-based internally.
    """

    os.makedirs(save_path, exist_ok=True)

    for rec_id, df in tqdm(selected_recordings.groupby("recording_id"), desc="Converting"):
        base_row = df.iloc[0]

        # Build output stem safely from first row (assumes consistent file_name/animal_position per group)
        base_name, _ = os.path.splitext(str(base_row[file_name_col]))
        edf_base = f"{base_name}_an{base_row[animal_position_col]}"
        txt_out = os.path.join(save_path, f"{edf_base}.txt")

        # Open LabChart once
        file_path = os.path.join(labchart_path, str(base_row[file_name_col]))
        try:
            fread = adi.read_file(file_path)
        except Exception as e:
            print(f"\n---> Could not open LabChart file for recording_id {rec_id}: {e}")
            continue

        # Collect ALL comments from the first record
        try:
            comments = fread.channels[0].records[0].comments
        except Exception as e:
            print(f"\n---> No comments found (or unreadable) for recording_id {rec_id}: {e}")
            del fread
            continue

        if not comments:
            print(f"\n---> No comments present, skipping recording_id {rec_id}")
            del fread
            continue

        # Flatten to DataFrame
        com_text = [c.text for c in comments]
        com_times = [c.time for c in comments]
        com_samples = [c.tick_position for c in comments]
        chan_ids = [c.channel_ for c in comments]  # 0-based in LabChart
        com_dt = [c.tick_dt for c in comments]

        com_df_all = pd.DataFrame(
            data=np.array([com_times, com_samples, chan_ids, com_dt]).T,
            columns=["com_time", "com_sample", "channel_id", "com_dt"],
            dtype=float,
        )
        com_df_all["com_text"] = com_text

        # Determine which channel IDs to include (convert Excel's 1-based -> 0-based)
        desired_channels_0b = set(int(x) - 1 for x in df[channel_id_col].values)
        com_df = com_df_all[com_df_all["channel_id"].isin(desired_channels_0b)].copy()

        if com_df.empty:
            print(f"\n---> No matching comments across ANY listed channels for recording_id {rec_id}")
            del fread
            continue

        # Convert to Visbrain hypnogram lines
        lines = comments_to_visbrain(com_df, state_map, add_initial_zero=True)
        del fread

        if not lines:
            print(f"\n---> Skipping recording_id {rec_id} due to unmapped labels")
            continue

        # Write output
        with open(txt_out, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


if __name__ == "__main__":
    # ------------------------------ USER SETTINGS ------------------------------ #
    # Parent path and key folders/files
    PARENT_PATH   = r"C:\temp_files_to_clean\sleep_scoring\scored_files_kj\train_new_scripts"
    LABCHART_PATH = os.path.join(PARENT_PATH, "labchart_data")   # Folder with .adicht files
    SAVE_PATH     = os.path.join(PARENT_PATH, "edf_data")        # Where to save .txt hypnograms
    EXCEL_FILE    = os.path.join(PARENT_PATH, "file_index.xlsx") # Excel with recording info

    # Map LabChart comment text -> Somnotate labels
    SOMNO_STATES = {
        "WAKE": "awake",
        "NREM": "non-REM",
        "REM":  "REM",
        "WAKJE": "awake",
        "WAKR":  "awake",
        "WAKE\\": "awake",
        "WALE":  "awake",
        "NEWM":  "non-REM",
        "WAKKE": "awake",
        "undefined": "undefined",
    }
    # ---------------------------------------------------------------------------- #

    # Load metadata
    meta = pd.read_excel(EXCEL_FILE)

    # Run conversion (collect comments from ALL channels listed for each recording)
    convert_annotations_any_channel(
        selected_recordings=meta,
        labchart_path=LABCHART_PATH,
        save_path=SAVE_PATH,
        state_map=SOMNO_STATES,
        animal_position_col="animal_position",
        file_name_col="file_name",
        channel_id_col="channel_id",
    )

    print("---> All hypnogram annotation files were created.")
