# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =============================================================================
#                               Somnotate Functions
# =============================================================================

# state_to_int = dict([
#     ('awake'              ,  1),
#     # ('awake (artefact)'   , -1),
#     # ('sleep movement'     ,  1),
#     ('non-REM'            ,  2),
#     # ('non-REM (artefact)' , -2),
#     ('REM'                ,  3),
#     # ('REM (artefact)'     , -3),
#     # ('undefined'          ,  0),
# ])

def load_hypnogram(file_path):
    """
    Load hypnogram given in visbrain Stage-duration format.

    Arguments:
    ----------
    file_path -- str
        /path/to/hypnogram/file.hyp

    Returns:
    --------
    states -- list of str
        List of annotated states.

    intervals -- list of (float start, float stop) tuples
        Corresponding time intervals.

    References:
    -----------
    http://visbrain.org/sleep.html#save-hypnogram
    """
    dtype = [('Stage', '|S30'), ('stop', float)]
    data = np.genfromtxt(file_path, skip_header=2, dtype=dtype, delimiter='\t')
    states = [state.astype(str).strip() for state in data['Stage']]
    transitions = np.r_[0, data['stop']]
    intervals = list(zip(transitions[:-1], transitions[1:]))
    return states, intervals

def convert_state_intervals_to_state_vector(states, intervals, mapping,
                                            time_resolution = 1.,
                                            length          = None,
):
    """
    Construct a state vector given a list of states and a corresponding list of intervals.

    Arguments:
    ----------
    states -- list of ints (or str if mapping is not None)
        The state vector.

    intervals -- list of (float start, float stop) tuples
        The contiguous intervals corresponding to each state in the state vector.

    mapping -- dict str : int
        The mapping from states in the state vector to integers.

    time_resolution -- float (default 1.)
       The assumed time duration of each entry in the state vector.

    Returns:
    --------
    state_vector -- (total samples, ) ndarray with dtype int
        The state vector.

    See also:
    ---------
    convert_state_vector_to_state_intervals
    """

    if time_resolution != 1:
        intervals = [(start/time_resolution, stop/time_resolution) for start, stop in intervals]

    if np.any([(isinstance(start, float), isinstance(stop, float)) for start, stop in intervals]):
        # breakpoint()
        # import warnings
        # warnings.warn("Interval values are converted from floats to integers.")
        # # round up last interval such that the state vector is guaranteed to include the last time point
        # last_start, last_stop = intervals[-1]
        # intervals[-1] = (last_start, np.ceil(last_stop))
        intervals = [(int(np.round(start)), int(np.round(stop))) for start, stop in intervals]

    if not length:
        length = np.max(intervals)

    state_vector = np.zeros((length), dtype=int)
    for state, (start, stop) in zip(states, intervals):
        state_vector[start:stop] = mapping[state]

    return state_vector

# =============================================================================
# =============================================================================

# plotting function
def get_color_for_stage(stage):
    color_mapping = {
        'awake': 'blue',       # Awake
        'non-REM': 'green',    # non-REM
        'REM': 'red'           # REM
    }
    return color_mapping.get(stage, 'black')

if __name__ == '__main__':
    
    # settings
    state_to_int = dict([
        ('awake'              ,  1),
        ('non-REM'            ,  2),
        ('REM'                ,  3),
    ])
    files = {'animal1': r"D:\scored_files_kj\pilot\processed\postCUS+SGE#5-8-1wk-11_6_20_an2_auto_state_annotation.hyp",
             'animal2': r"D:\scored_files_kj\pilot\processed\postCUS+SGE#5-8-1wk-11_6_20_an4_auto_state_annotation.hyp"}
    
    # loop through animals
    int_to_state = {v: k for k, v in state_to_int.items()}
    data_list = []
    state_list = {}
    for animal_id in files:
        # load hypnogram and convert to sleep state vector
        states, intervals = load_hypnogram(files[animal_id])
        state_vector = convert_state_intervals_to_state_vector(states, intervals, time_resolution=1, mapping=state_to_int)
        
        # add vector for each animal to dataframe
        df = pd.DataFrame({'time_sec': np.arange(len(state_vector)),
                           'sleep_state': state_vector})
        df['animal_id'] = animal_id
        df['sleep_stage'] = df['sleep_state'].map(int_to_state)
        data_list.append(df)
        state_list.update({animal_id:states})
        
    # create data across animals
    data = pd.concat(data_list).reset_index(drop=True)
    data['time_hours'] = pd.to_datetime(data['time_sec'], unit='h', utc=True)
    data['time_hours'] = pd.to_datetime(data['time_sec'], unit='s').dt.strftime('%H:%M:%S')
    
    # add experiment onset time to convert to 12 hour format
    start_time = pd.to_datetime('13:30:00', format='%H:%M:%S')
    data['time_am_pm'] = (start_time + pd.to_timedelta(data['time_sec'], unit='s')).dt.strftime('%I:%M:%S %p')

    # plot percent time in each sleep state
    sleep_df = data.groupby(['animal_id', 'sleep_stage'])['time_sec'].count().reset_index()
    sleep_df['total_time'] = sleep_df.groupby('animal_id')['time_sec'].transform('sum')
    sleep_df['percent_time'] = 100 * sleep_df['time_sec'] / sleep_df['total_time']
    sns.catplot(data=sleep_df, hue='animal_id', y='percent_time', x='sleep_stage', kind='bar')
    
    # Plot state transitions
    pivot_data = data.pivot(index='animal_id', columns='time_hours', values='sleep_state')
    plt.figure(figsize=(12, 6))
    sns.heatmap(pivot_data)
    
    # count transitions
    transition_list = []
    for animal_id in state_list:
        transitions = state_list[animal_id]
        # sleep_state = [state_to_int[sleep_stage] for sleep_stage in sleep_stages]
        pairs = [f'{transitions[i]} -> {transitions[i + 1]}' for i in range(len(transitions) - 1)]
        df = pd.DataFrame({'transition_pair':pairs, 'animal_id':np.repeat(animal_id, len(pairs))})
        transition_list.append(df)
    transition_df = pd.concat(transition_list).reset_index(drop=True)
    plt.figure(figsize=(12, 6))
    sns.histplot(data=transition_df, x='transition_pair', hue='animal_id', multiple="dodge", shrink=.8, stat='probability')
    
    # number of bouts
    bout_df_list = []
    for animal_id in state_list:
       df = pd.DataFrame({'sleep_stage':state_list[animal_id], 'animal_id':np.repeat(animal_id, len(state_list[animal_id]))})
       bout_df_list.append(df)
    bout_df =  pd.concat(bout_df_list).reset_index(drop=True)
    plt.figure(figsize=(12, 6))
    sns.countplot(data=bout_df, x='sleep_stage', hue='animal_id',)
       
    # bout duration
    data['state_change'] = (data['sleep_stage'] != data['sleep_stage'].shift()).cumsum()
    data['cumulative_time'] = data.groupby(['animal_id', 'state_change']).cumcount() + 1
    bout_length_df = data.groupby(['animal_id', 'sleep_stage', 'state_change'])['cumulative_time'].max().reset_index()
    # bout_length_df = bout_length_df.groupby(['animal_id', 'sleep_stage',])['cumulative_time'].mean().reset_index()
    sns.catplot(data=bout_length_df, x='sleep_stage', hue='animal_id', y='cumulative_time', kind='bar', errorbar='se')
   



