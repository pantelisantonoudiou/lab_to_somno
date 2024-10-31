# -*- coding: utf-8 -*-

# imports
import os
from plot_sleep_states import load_hypnogram, convert_state_intervals_to_state_vector
from sklearn.metrics import balanced_accuracy_score, accuracy_score, cohen_kappa_score

# settings
state_to_int = dict([
    ('awake'              ,  1),
    ('non-REM'            ,  2),
    ('REM'                ,  3),
    ('undefined'          ,  -1)
])
files = {r"D:\scored_files_kj\test_model\raw_data\preCUS#5-8-10_9_20_1_an2.txt": r"D:\scored_files_kj\test_model\processed\preCUS#5-8-10_9_20_1_an2_auto_state_annotation.hyp",
         r"D:\scored_files_kj\test_model\raw_data\preCUS#5-8-10_9_20_2_an4.txt": r"D:\scored_files_kj\test_model\processed\preCUS#5-8-10_9_20_2_an4_auto_state_annotation.hyp"}

# loop through animals
int_to_state = {v: k for k, v in state_to_int.items()}
data_list = []
state_list = {}
for manual_annotation, auto_annotation in files.items():
    
    # manual
    states, intervals = load_hypnogram(manual_annotation)
    manual_vector = convert_state_intervals_to_state_vector(states, intervals, time_resolution=1, mapping=state_to_int)
    
    # auto
    states, intervals = load_hypnogram(auto_annotation)
    auto_vector = convert_state_intervals_to_state_vector(states, intervals, time_resolution=1, mapping=state_to_int)
    
    filename = os.path.normpath(manual_annotation).split(os.sep)[-1][:-4]
    accuracy = accuracy_score(manual_vector, auto_vector)
    balanced_accuracy = balanced_accuracy_score(manual_vector, auto_vector)
    kappa = cohen_kappa_score(manual_vector, auto_vector)
    print(f'\n--> Accuracy:{accuracy} -- for {filename}.')
    print(f'--> Balanced Accuracy:{balanced_accuracy} -- for {filename}.')
    print(f'--> kappa:{kappa} -- for {filename}.')