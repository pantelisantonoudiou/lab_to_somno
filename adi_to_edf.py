# -*- coding: utf-8 -*-

#### -------------------------- Imports -------------------------- ####
import os
import adi
import pyedflib
import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy.signal import decimate
#### ------------------------------------------------------------- ####


def save_to_edf(save_path, data, channel_properties):
    """
    Write multi-channel data to an EDF file with the provided channel metadata.

    Parameters
    ----------
    save_path : str
        Full path (including filename.edf) to write the EDF file.
    data : list[np.ndarray]
        One array per channel, all with the same length (samples per channel).
    channel_properties : dict
        Dict containing metadata for each channel. Required keys (all lists):
            - "sample_rate", "channel_name", "dimension",
              "physical_max", "physical_min", "digital_max", "digital_min"

    Raises
    ------
    Exception
        If number of channels in `data` does not match metadata lengths.
    """

    n_channels = len(channel_properties["channel_name"])
    if len(data) != n_channels:
        raise Exception("--> Channel count mismatch between data and metadata.")

    # Validate metadata lengths
    for k in channel_properties:
        if len(channel_properties[k]) != n_channels:
            raise Exception(f"--> channel_properties['{k}'] length != n_channels.")

    # Build EDF signal headers
    channel_info = []
    for i in range(n_channels):
        channel_dict = {
            "sample_rate": channel_properties["sample_rate"][i],
            "label": channel_properties["channel_name"][i],
            "dimension": channel_properties["dimension"][i],
            "physical_max": channel_properties["physical_max"][i],
            "physical_min": channel_properties["physical_min"][i],
            "digital_max": channel_properties["digital_max"][i],
            "digital_min": channel_properties["digital_min"][i],
        }
        channel_info.append(channel_dict)

    # Write EDF file
    with pyedflib.EdfWriter(save_path, n_channels, file_type=pyedflib.FILETYPE_EDF) as edf:
        edf.setSignalHeaders(channel_info)
        edf.writeSamples(data)


def process_recordings(selected_recordings, load_path, save_path, block, channel_properties):
    """
    Process all recordings listed in the metadata DataFrame, convert LabChart data to EDF.

    Parameters
    ----------
    selected_recordings : pd.DataFrame
        Metadata for all recordings (must include columns: recording_id, file_name,
        channel_name, channel_id, start_time_sec, stop_time_sec, animal_position).
    load_path : str
        Directory containing LabChart input files.
    save_path : str
        Directory to save EDF files (created if missing).
    block : int
        LabChart block index to read.
    channel_properties : dict
        EDF channel settings (see save_to_edf docstring).
    """

    os.makedirs(save_path, exist_ok=True)

    for rec_id, df in tqdm(selected_recordings.groupby('recording_id')):

        # Pick representative row (prefer BLA channel, else first row)
        bla_rows = df[df['channel_name'].str.contains('BLA', case=False, na=False)]
        base_row = bla_rows.iloc[0] if len(bla_rows) else df.iloc[0]

        raw_name = os.path.splitext(base_row['file_name'])[0]
        animal_pos = str(base_row.get('animal_position', 'NA'))
        edf_file_name = f"{raw_name}_an{animal_pos}.edf"

        # Open LabChart file and determine sampling info
        file_path = os.path.join(load_path, base_row['file_name'])
        fread = adi.read_file(file_path)
        fs = float(fread.channels[0].fs[0])
        target_sr = float(channel_properties['sample_rate'][0])
        downsample_factor = int(round(fs / target_sr))

        # Collect and downsample all channels
        ch_data = []
        for channel in channel_properties['channel_name']:
            ch_id = int(df.loc[df['channel_name'] == channel, 'channel_id'].values[0])
            start = int(df.loc[df['channel_name'] == channel, 'start_time_sec'].values[0] * fs)
            stop  = int(df.loc[df['channel_name'] == channel, 'stop_time_sec'].values[0]  * fs)
            stop = fread.records[0].n_ticks + stop

            raw = fread.channels[ch_id - 1].get_data(block, start_sample=start, stop_sample=stop)

            # Trim to multiple of downsample factor
            trim_len = (len(raw) // downsample_factor) * downsample_factor
            downsampled = decimate(raw[:trim_len], downsample_factor, zero_phase=True)

            ch_data.append(downsampled)

        del fread  # free handle

        # Ensure all channels equal length
        min_len = min(map(len, ch_data))
        ch_data = [x[:min_len] for x in ch_data]

        # Save to EDF
        save_to_edf(os.path.join(save_path, edf_file_name), ch_data, channel_properties)


if __name__ == '__main__':

    # ------------------------- User Settings -------------------------
    load_path = r"D:\sleep_scoring\cus_files\labchart_data"             # Folder with LabChart files
    save_path = r"D:\sleep_scoring\cus_files\raw_data"                  # Output folder for EDF files
    recording_path = r"D:\sleep_scoring\cus_files\CUS_file_info.xlsx"   # Excel with recording info
    block = 1                                                           # LabChart block index

    # Channel properties (edit as needed)
    channel_properties = {
        "sample_rate":  [250, 250, 250],
        "channel_name": ["BLA-LFP", "FC-EEG", "EMG"],
        "dimension":    ["V", "V", "V"],
        "physical_max": [0.1, 0.1, 0.01],
        "physical_min": [-0.1, -0.1, -0.01],
        "digital_max":  [32000, 32000, 32000],
        "digital_min":  [-32000, -32000, -32000],
    }
    # -----------------------------------------------------------------

    # Read metadata and process recordings
    selected_recordings = pd.read_excel(excel_file)
    process_recordings(selected_recordings, load_path, save_path, block, channel_properties)
    print('---> All files were converted to EDF.')