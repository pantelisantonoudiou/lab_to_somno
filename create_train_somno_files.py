# -*- coding: utf-8 -*-
"""
Pipeline runner:
1) Create hypnogram .txt files from comments (all channels listed in Excel).
2) Convert LabChart .adicht -> EDF (trim to hypnogram duration) for training.
3) Build Somnotate TRAINING CSV that references EDF + hypnograms.

Usage:
  python run_pipeline.py
"""

import os
import pandas as pd

# --- Ensure these module filenames exist next to this script ---
from convert_to_visbrain import convert_annotations_any_channel
from adi_to_edf_train import process_training_recordings
from create_somno_train import create_somno_train_csv


def run_pipeline(
    parent_path: str,
    excel_file: str,
    labchart_path: str,
    hypnogram_out_path: str,
    edf_out_path: str,
    processed_path: str,
    csv_out_path: str,
    somno_states: dict,
    channel_properties: dict,
    channel_labels: list,
    sample_rate: int,
    block_index: int = 1,
    animal_position_col: str = "animal_position",
    file_name_col: str = "file_name",
    channel_id_col: str = "channel_id",
    comment_channel_hint: str = "BLA",
    require_hypnogram: bool = True,
    ):
    # Create output dirs
    os.makedirs(hypnogram_out_path, exist_ok=True)
    os.makedirs(edf_out_path, exist_ok=True)
    os.makedirs(processed_path, exist_ok=True)
    os.makedirs(os.path.dirname(csv_out_path), exist_ok=True)

    # Load metadata (Excel)
    if not os.path.exists(excel_file):
        raise FileNotFoundError(f"Excel file not found:\n  {excel_file}")
    meta = pd.read_excel(excel_file)

    # Step 1: Hypnograms from comments (all channels in Excel)
    print("\n[1/3] Creating hypnogram .txt files from comments...")
    convert_annotations_any_channel(
        selected_recordings=meta,
        labchart_path=labchart_path,
        save_path=hypnogram_out_path,
        state_map=somno_states,
        animal_position_col=animal_position_col,
        file_name_col=file_name_col,
        channel_id_col=channel_id_col,
    )
    print("    ✓ Hypnogram generation finished.")

    # Step 2: LabChart -> EDF using hypnogram duration
    print("\n[2/3] Converting LabChart -> EDF (trim to hypnogram duration)...")
    process_training_recordings(
        selected_recordings=meta,
        labchart_path=labchart_path,
        score_path=hypnogram_out_path,    # where .txt hypnograms were written
        edf_out_path=edf_out_path,        # where .edf will be written
        block=block_index,
        channel_properties=channel_properties,
        comment_channel_hint=comment_channel_hint,
    )
    print("    ✓ EDF conversion finished.")

    # Step 3: Build Somnotate TRAINING CSV
    print("\n[3/3] Building Somnotate TRAINING CSV...")
    create_somno_train_csv(
        raw_path=edf_out_path,            # EDF + .txt live together here
        processed_path=processed_path,    # Somnotate outputs will go here
        save_path=csv_out_path,           # final CSV path
        channel_labels=channel_labels,    # ["BLA-LFP", "FC-EEG", "EMG"]
        sample_rate=sample_rate,          # e.g., 250
        require_hypnogram=require_hypnogram,
    )
    print("    ✓ Training CSV created.")

    print("\nPipeline complete.")


if __name__ == "__main__":
    # ------------------------------ USER SETTINGS ------------------------------ #
    PARENT_PATH       = r"C:\temp_files_to_clean\sleep_scoring\scored_files_kj\train_new_scripts"
    EXCEL_FILE        = os.path.join(PARENT_PATH, "file_index.xlsx")

    LABCHART_PATH     = os.path.join(PARENT_PATH, "labchart_data")        # .adicht files
    HYPNOGRAM_OUT     = os.path.join(PARENT_PATH, "edf_data")             # .txt hypnograms
    EDF_OUT           = os.path.join(PARENT_PATH, "edf_data")             # .edf output
    PROCESSED_PATH    = os.path.join(PARENT_PATH, "processed")            # Somnotate outputs
    CSV_OUT           = os.path.join(PARENT_PATH, "somno_input_for_train.csv")

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

    # Channel properties for the TARGET (downsampled) EDF
    CHANNEL_PROPERTIES = {
        "sample_rate":  [250, 250, 250],
        "channel_name": ["BLA-LFP", "FC-EEG", "EMG"],
        "dimension":    ["V", "V", "V"],
        "physical_max": [0.1, 0.1, 0.01],
        "physical_min": [-0.1, -0.1, -0.01],
        "digital_max":  [32000, 32000, 32000],
        "digital_min":  [-32000, -32000, -32000],
    }

    CHANNEL_LABELS = ["BLA-LFP", "FC-EEG", "EMG"]  # must match EDF channel order
    SAMPLE_RATE    = 250
    BLOCK_INDEX    = 1
    COMMENT_CHANNEL_HINT = "BLA"  # used only for EDF filename choice
    REQUIRE_HYPNOGRAM    = True
    # ---------------------------------------------------------------------------- #

    run_pipeline(
        parent_path=PARENT_PATH,
        excel_file=EXCEL_FILE,
        labchart_path=LABCHART_PATH,
        hypnogram_out_path=HYPNOGRAM_OUT,
        edf_out_path=EDF_OUT,
        processed_path=PROCESSED_PATH,
        csv_out_path=CSV_OUT,
        somno_states=SOMNO_STATES,
        channel_properties=CHANNEL_PROPERTIES,
        channel_labels=CHANNEL_LABELS,
        sample_rate=SAMPLE_RATE,
        block_index=BLOCK_INDEX,
        comment_channel_hint=COMMENT_CHANNEL_HINT,
        require_hypnogram=REQUIRE_HYPNOGRAM,
    )
