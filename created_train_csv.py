# -*- coding: utf-8 -*-


import os
import numpy as np
import pandas as pd


# required columns
columns = ['file_path_raw_signals',
         'eeg1_signal_label',
         'eeg2_signal_label',
         'emg_signal_label',
         'sampling_frequency_in_hz',
         'file_path_preprocessed_signals',
         'file_path_manual_state_annotation',
         'file_path_automated_state_annotation',
         'file_path_refined_state_annotation',
         'file_path_review_intervals',
         'file_path_manual_artefact_annotation',
         'file_path_automated_artefact_annotation',
         'file_path_artefact_intervals',
         'file_path_missing_value_intervals']

# get edf files
raw_path = r"D:\scored_files_kj\train_model\raw_data"
processed_path = r"D:\scored_files_kj\train_model\processed"
edf_files = [file for file in os.listdir(raw_path) if file[-4:] == '.edf']

# create dataframe
data = []
for edf_file in edf_files:
    row = []
    
    # file_path_raw_signals
    row.append(os.path.join(raw_path, edf_file))
    
    # 3 channel labels
    row.append('BLA-LFP')
    row.append('FC-EEG')
    row.append('EMG')
    
    # sampling_frequency_in_hz
    row.append(400)
    
    # file_path_preprocessed_signals
    row.append(os.path.join(processed_path, edf_file[:-4] +  '.npy'))
    
    # file_path_manual_state_annotation
    row.append(os.path.join(raw_path, edf_file[:-4] +  '_score.txt'))
    
    # file_path_automated_state_annotation
    row.append(os.path.join(processed_path, edf_file[:-4] +  '_auto_state_annotation.hyp'))
    
    # file_path_refined_state_annotation
    row.append(os.path.join(processed_path, edf_file[:-4] +  '_refined_state_annotation.hyp'))
    
    # file_path_review_intervals
    row.append(os.path.join(processed_path, edf_file[:-4] +  '_review_intervals.csv'))
    
    # file_path_manual_artefact_annotation
    row.append('')
    
    # file_path_automated_artefact_annotation
    row.append(os.path.join(processed_path, edf_file[:-4] +  '_automated_artefact_annotation.hyp'))
    
    # file_path_artefact_intervals
    row.append(os.path.join(processed_path, edf_file[:-4] +  '_artefact_intervals.csv'))
    
    # file_path_missing_value_intervals
    row.append(os.path.join(processed_path, edf_file[:-4] +  '_missing_value_intervals.csv'))
    
    # append to data
    data.append(row)
    
df = pd.DataFrame(data=np.array(data), columns=columns)
df.to_csv(r"D:\scored_files_kj\train_model\input_for_train.csv", index=False)
    
    
    
    
    
