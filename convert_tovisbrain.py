# -*- coding: utf-8 -*-

#### -------------------------- Imports -------------------------- ####
import adi
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
#### ------------------------------------------------------------- ####

def lab_to_vis_scores(com_df, somno_states):
    """
    Converts lab comments to Visbrain scoring format by mapping comment text 
    to corresponding somnotate labels and capturing state transitions.
    
    Parameters
    ----------
    ch_comments : df, comment df
    somno_states : dict, mapping labchart comments to corresponding somnotate states (values).
    
    Returns
    -------
    visbrain_data : list
        A list of strings formatted for Visbrain. Each element represents a 
        state transition or relevant header information. Returns 'True' if 
        mismatched labels are found.
    
    Notes
    -----
    - If any label from the lab comments does not match the provided somno_states, 
      it will print a warning and return True without completing the conversion.
      """

    # convert comments to somnotate labels
    somno_labels = [somno_states.get(e, e) for e in com_df['com_text'].values]
    com_times = com_df['com_time'].values
    
    # check if labels match
    if not set(somno_labels) <= set(somno_states.values()):
        print('--> Some labels seem to be incorrect', set(somno_labels))
        return True
        
    # Initialize a list to store the Visbrain format data
    visbrain_data = []
    
    # add duration to the nearest 10 samples to allow downsampling
    file_duration = np.ceil(com_times[-1])
    visbrain_data.append(f"*Duration_sec\t{file_duration}")
    visbrain_data.append("*Datafile\tUnspecified")
    
    # Iterate over the dataframe to capture state transitions
    for com_txt, com_time in zip(somno_labels[:-1], com_times[1:]):
            visbrain_data.append(f"{com_txt}\t{com_time}")
    
    # if file longer than last comment time add undefined period
    if file_duration > com_times[-1]:
        visbrain_data.append(f"undefined\t{file_duration}")
    
    return visbrain_data

if __name__ == '__main__':
    
    # get settings and read excel file with paths
    main_path = r"D:\scored_files_kj\train_model_all\labchart_data"
    save_path = r"D:\scored_files_kj\train_model_all\raw_data"
    selected_recordings = pd.read_excel(r"D:\scored_files_kj\train_model_all\selected_recordings.xlsx")
    somno_states = {'WAKE':'awake', 'NREM':'non-REM', 'REM':'REM',
                    'WAKJE':'awake', 'WAKR':'awake', 'WAKE\\':'awake',
                    'WALE':'awake', 'NEWM':'non-REM', 'WAKKE':'awake',
                    'undefined':'undefined'}    

    # iterate
    for cond, df in tqdm(selected_recordings.groupby('recording_id')):
        
        # find row that contains comments(BLA)
        row_dict = df[df['channel_name'].str.contains('BLA')].to_dict('records')[0]
        file_path = os.path.join(main_path, row_dict['file_name'])
        
        # load labchart file and convert comments to dataframe
        fread = adi.read_file(file_path)
        ch_comments = fread.channels[0].records[0].comments
        com_text = [x.text for x in ch_comments]
        com_times = [x.time for x in ch_comments]
        com_samples = [x.tick_position for x in ch_comments]
        channel_id = [x.channel_ for x in ch_comments]
        com_dt = [x.tick_dt for x in ch_comments]
        com_df = pd.DataFrame(data = np.array([com_times, com_samples, channel_id, com_dt]).T,
                              columns=['com_time', 'com_sample', 'channel_id', 'com_dt'], dtype=float)
        com_df['com_text'] = com_text

        # filter the channel in df and convert those comments
        com_df = com_df[com_df['channel_id'] == row_dict['channel_id']-1]
        if len(com_df) == 0: # skip if no comments
            print(f'\n---> No comments were found skipping recording {cond}')
            continue
        visbrain_data = lab_to_vis_scores(com_df, somno_states)
    
        # Write the output to a text file
        file_name = f"{row_dict['file_name'][:-7]}_an{row_dict['animal_position']}.txt"
        with open(os.path.join(save_path, file_name), 'w') as f:
            for line in visbrain_data:
                f.write(line + '\n')
