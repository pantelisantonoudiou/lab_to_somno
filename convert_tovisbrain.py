# -*- coding: utf-8 -*-

#### -------------------------- Imports -------------------------- ####
import adi
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
#### ------------------------------------------------------------- ####

def lab_to_vis_scores(ch_comments, somno_states):
    """
    Converts lab comments to Visbrain scoring format by mapping comment text 
    to corresponding somnotate labels and capturing state transitions.
    
    Parameters
    ----------
    ch_comments : list
        A list of objects, where each object contains a 'text' attribute for 
        the comment and a 'time' attribute for the timestamp of the comment.
    somno_states : dict
        A dictionary mapping the text of lab comments (keys) to corresponding 
        somnotate states (values).
    
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
    
    # get comments and comment times
    com_text = [x.text for x in ch_comments]
    com_times = [x.time for x in ch_comments]
    
    # convert comments to somnotate labels
    somno_labels = [somno_states.get(e, e) for e in com_text]
    
    # check if labels match
    if set(somno_labels) != set(somno_states.values()):
        print('--> Some labels seem to be incorrect', set(somno_labels))
        return True
        
    # Initialize a list to store the Visbrain format data
    visbrain_data = []
    
    # add duration to the nearest 10 samples to allow downsampling
    last_sample = ch_comments[-1].tick_position
    duration = (last_sample + last_sample%10) * ch_comments[-1].tick_dt
    visbrain_data.append(f"*Duration_sec\t{duration}")
    visbrain_data.append("*Datafile\tUnspecified")
    
    # Iterate over the dataframe to capture state transitions
    for com_txt, com_time in zip(somno_labels[:-1], com_times[1:]):
            visbrain_data.append(f"{com_txt}\t{com_time}")
            
    if duration > com_times[-1]:
        visbrain_data.append(f"'Undefined\t{duration}")
    
    return visbrain_data

if __name__ == '__main__':
    
    # get settings and read excel file with paths
    main_path = r"D:\scored_files_kj\labchart_data"
    save_path = r"D:\scored_files_kj\somno_data"
    somno_states = {'WAKE':'awake', 'NREM':'non-REM', 'REM':'REM',
                    'WAKJE':'awake', 'WAKR':'awake', 'WAKE\\':'awake',
                    'WALE':'awake', 'NEWM':'non-REM', 'WAKKE':'awake'}    
    df = pd.read_excel(r"D:\scored_files_kj\selected_recordings KJ.xlsx")
    
    for cond, df in tqdm(df.groupby('recording_id'), total=len(df['recording_id'].unique())):
        
        # find row that contains comments(BLA)
        row_dict = df[df['channel_name'].str.contains('BLA')].to_dict('records')[0]
        file_path = os.path.join(main_path, row_dict['file_name'])
        
        # load labchart file and convert comments to visbrain format
        fread = adi.read_file(file_path)
        ch_comments = fread.channels[row_dict['channel_id']].records[0].comments
        visbrain_data = lab_to_vis_scores(ch_comments, somno_states)
    
        # Write the output to a text file
        file_name = f"{row_dict['file_name'][:-7]}_an{row_dict['animal_position']}.txt"
        with open(os.path.join(save_path, file_name), 'w') as f:
            for line in visbrain_data:
                f.write(line + '\n')
