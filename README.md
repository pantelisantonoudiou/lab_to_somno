# lab_to_somno
## Overview
This repository provides tools for processing, converting, and analyzing sleep scoring data. It includes scripts for converting LabChart data to EDF format, generating input CSVs for Somnotate, and analyzing sleep states. The repository is designed to streamline workflows for sleep research and facilitate data preparation for machine learning models.

---

## Repository Structure
| File Name               | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| `adi_to_edf.py`          | Converts LabChart data to EDF format for CUS files.                        |
| `adi_to_edf_train.py`    | Converts LabChart data to EDF format for training files.                   |
| `convert_tovisbrain.py`  | Converts LabChart comments to Visbrain hypnogram format.                   |
| `create_somno_csv.py`    | Generates CSV input files for Somnotate analysis (CUS files).              |
| `created_train_csv.py`   | Generates CSV input files for Somnotate training (all files).              |
| `plot_sleep_states.py`   | Plots sleep states and transitions from hypnogram files.                   |
| `read_edf.py`            | Example script for reading EDF files.                                      |
| `test_accuracy.py`       | Compares manual and automated sleep state annotations for accuracy.        |

---

## Installation
```sh
git clone https://github.com/your-repo/lab_to_somno.git
cd lab_to_somno
pip install -r requirements.txt
```
Ensure you have access to the required data files and update paths in the scripts as needed.

---

## Usage

### 1. Convert LabChart Data to EDF
- **CUS files**: Run `adi_to_edf.py` to convert LabChart data to EDF format. Update the `load_path` and `save_path` variables in the script.  
- **Training files**: Run `adi_to_edf_train.py` to convert LabChart data for training.

### 2. Convert LabChart Comments to Visbrain Format
Run `convert_tovisbrain.py` to generate hypnogram text files compatible with Visbrain. Update the `main_path` and `save_path` variables.

### 3. Generate Input CSVs
- **CUS files**: Run `create_somno_csv.py` to generate CSV files for Somnotate analysis.  
- **Training files**: Run `created_train_csv.py` to generate CSV files for Somnotate training.

### 4. Plot Sleep States
Run `plot_sleep_states.py` to visualize sleep state distributions, transitions, and bout durations. Uses Seaborn and Matplotlib.

### 5. Test Annotation Accuracy
Run `test_accuracy.py` to compare manual and automated sleep state annotations. Calculates accuracy, balanced accuracy, and Cohen’s kappa score.

### 6. Read EDF Files
Use `read_edf.py` as an example to read EDF files and extract signal data.

---

## Example Workflow
1. Convert LabChart data to EDF format (`adi_to_edf.py` or `adi_to_edf_train.py`).  
2. Generate hypnogram files (`convert_tovisbrain.py`).  
3. Create input CSVs for Somnotate (`create_somno_csv.py` or `created_train_csv.py`).  
4. Analyze sleep states and transitions (`plot_sleep_states.py`).  
5. Evaluate annotation accuracy (`test_accuracy.py`).  

---

## Dependencies
```txt
numpy
pandas
matplotlib
seaborn
pyedflib
tqdm
scikit-learn
```