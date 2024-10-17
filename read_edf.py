# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 15:32:59 2024

@author: pante
"""

import numpy as np
import pyedflib
import matplotlib.pyplot as plt

fread = pyedflib.EdfReader(r"D:\scored_files_kj\somno_data\postCUS#5-8-24hr-11_30_20_an2.edf")
# channel_labels = fread.getSignalLabels()
fs = int(fread.getSampleFrequencies()[0])
# sig = fread.readSignal(chn=0)
# del fread
fread.getNSamples()[0]/fs

# t = np.arange(sig.shape[0])/fs
# # plt.plot(t, sig)
