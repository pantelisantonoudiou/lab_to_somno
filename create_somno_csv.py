# -*- coding: utf-8 -*-
"""
Create Somnotate input CSV from EDF files.

This script scans a folder of EDF files and generates a CSV file
that specifies the raw signals, labels, sample rate, and paths
to processed/annotation files.

User should only need to configure the SETTINGS section.
"""

import os
import numpy as np
import pandas as pd


def create_somno_csv(
    raw_path,
    processed_path,
    save_path,
    channel_labels,
    sample_rate,
):
    """
    Generate Somnotate input CSV.

    Parameters
    ----------
    raw_path : str
        Directory containing EDF files.
    processed_path : str
        Directory where processed files and annotations will be stored.
    save_path : str
        Full path (CSV file) to save the output.
    channel_labels : list[str]
        Labels for EEG/EMG channels (length must match EDF channels).
    sample_rate : int
        Sampling frequency in Hz.
    """

    # required columns for Somnotate input
    columns = [
        "file_path_raw_signals",
        "eeg1_signal_label",
        "eeg2_signal_label",
        "emg_signal_label",
        "sampling_frequency_in_hz",
        "file_path_preprocessed_signals",
        "file_path_manual_state_annotation",
        "file_path_automated_state_annotation",
        "file_path_refined_state_annotation",
        "file_path_review_intervals",
        "file_path_manual_artefact_annotation",
        "file_path_automated_artefact_annotation",
        "file_path_artefact_intervals",
        "file_path_missing_value_intervals",
    ]

    # collect EDF files
    edf_files = [f for f in os.listdir(raw_path) if f.lower().endswith(".edf")]
    if not edf_files:
        raise FileNotFoundError(f"No EDF files found in {raw_path}")

    data = []
    for edf_file in edf_files:
        base = os.path.splitext(edf_file)[0]

        row = [
            os.path.join(raw_path, edf_file),                           # file_path_raw_signals
            channel_labels[0],                                          # eeg1_signal_label
            channel_labels[1],                                          # eeg2_signal_label
            channel_labels[2],                                          # emg_signal_label
            sample_rate,                                                # sampling_frequency_in_hz
            os.path.join(processed_path, f"{base}.npy"),                # preprocessed signals
            "",                                                         # manual state annotation
            os.path.join(processed_path, f"{base}_auto_state_annotation.hyp"),
            os.path.join(processed_path, f"{base}_refined_state_annotation.hyp"),
            os.path.join(processed_path, f"{base}_review_intervals.csv"),
            "",                                                         # manual artefact annotation
            os.path.join(processed_path, f"{base}_automated_artefact_annotation.hyp"),
            os.path.join(processed_path, f"{base}_artefact_intervals.csv"),
            os.path.join(processed_path, f"{base}_missing_value_intervals.csv"),
        ]

        data.append(row)

    df = pd.DataFrame(data=np.array(data), columns=columns)


    # ensure output dir exists
    os.makedirs(processed_path, exist_ok=True)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_csv(save_path, index=False)

    print(f"---> Somnotate input CSV created: {save_path}")
    print(f"     {len(edf_files)} EDF files processed.")


if __name__ == "__main__":
    # ------------------------- USER SETTINGS ------------------------- #
    PARENT_PATH = r"C:\temp_files_to_clean\sleep_scoring\pilot_test"
    EDF_PATH = os.path.join(PARENT_PATH, 'edf_data')             # folder with EDF files
    PROCESSED_PATH = os.path.join(PARENT_PATH, 'processed')      # folder for processed/annotation files
    CSV_PATH = os.path.join(PARENT_PATH, 'somno_input.csv')      # output CSV
    SAMPLE_RATE = 250                                            # Hz
    CHANNEL_LABELS = ["BLA-LFP", "FC-EEG", "EMG"]                # must be 3 labels
    # ---------------------------------------------------------------- #

    create_somno_csv(
        raw_path=EDF_PATH,
        processed_path=PROCESSED_PATH,
        save_path=CSV_PATH,
        channel_labels=CHANNEL_LABELS,
        sample_rate=SAMPLE_RATE,
    )
