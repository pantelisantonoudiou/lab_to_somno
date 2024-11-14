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
    Saves data to edf file together with channel properties

    Parameters
    ----------
    save_path : str, path to save edf file
    data : array, 2d array, (time, channels)
    channel_properties : dict with channel properties required for the df file

    Raises
    ------
    Exception: Raises Exception if number of channels in data does not match length of channel_properties['channel_id']

    Returns
    -------
    None.

    """
    
    # Convert channel_properties to channel info
    if len(ch_data) != len(channel_properties['channel_name']):
        raise Exception('--> Warning channels in data do not match channels in channel_properties dict.')
    channel_info = []
    for i in range(len(channel_properties["sample_rate"])):
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

    # save channel info and data to edf file
    with pyedflib.EdfWriter(save_path, len(data), file_type=pyedflib.FILETYPE_EDF) as edf:
        edf.setSignalHeaders(channel_info)
        edf.writeSamples(data)
        edf.close()
        
        
if __name__ == '__main__':
    
    # settings
    load_path = r"D:\sleep_scoring\scored_files_kj\train_model_all\labchart_data"
    save_path = r"D:\sleep_scoring\scored_files_kj\train_model_all\raw_data"
    block = 1
    
    # read df with selected recordings
    selected_recordings = pd.read_excel(r"D:\sleep_scoring\scored_files_kj\train_model_all\selected_recordings.xlsx")
    
    # edf settings with downsampled rate
    channel_properties = {
           "sample_rate" : [250, 250, 250],
           "channel_name":  ["BLA-LFP","FC-EEG","EMG"],
           "dimension": ["V","V","V"],
           "physical_max": [0.1, 0.1, 0.01],
           "physical_min": [-0.1, -0.1, -0.01],
           "digital_max": [32000, 32000, 32000],
           "digital_min": [-32000, -32000, -32000],
           }
    

    for i, df in tqdm(selected_recordings.groupby('recording_id')):
        
        # if associated score file exists load it and proceed with conversion
        row_dict = df[df['channel_name'].str.contains('BLA')].to_dict('records')[0]
        edf_file_name = f"{row_dict['file_name'][:-7]}_an{row_dict['animal_position']}.edf"
        score_file_path = os.path.join(save_path, f"{edf_file_name[:-4]}.txt")
        if not os.path.exists(score_file_path):
            print(f"\n---> Path not found, skipping recording id {i}")
            continue
        score_df = pd.read_csv(score_file_path, header=None)
        
        # get stop time for each recordings based on last comment
        file_path = os.path.join(load_path, row_dict['file_name'])
        fread = adi.read_file(file_path)
        fs = fread.channels[0].fs[0]
        stop_sample = int(float(score_df.iloc[0].values[0].split('\t')[1]) * fs)
        downsample_factor = int(fs/channel_properties['sample_rate'][0])

        # read and downsample labchart data
        ch_data = []
        for channel in channel_properties['channel_name']:
            ch_id = df.loc[df['channel_name'] == channel, 'channel_id'].values[0]
            single_channel_data = fread.channels[ch_id-1].get_data(block, start_sample=1, stop_sample=stop_sample)
            downsampled = decimate(single_channel_data, downsample_factor)
            ch_data.append(downsampled)
        del fread
        
        # rewrite to edf file
        save_to_edf(os.path.join(save_path, edf_file_name), ch_data, channel_properties)
    print('---> All files were converted to edf.')