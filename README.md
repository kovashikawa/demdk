# demdk - data engineering @ modak
> this repo consists of a technical exercise for the data engineering position at [modak](https://modak.na.teamtailor.com/)

the complete exercise description can be found at the [data-challenge.pdf](https://github.com/kovashikawa/demdk/blob/main/data-challenge.pdf)

the solution and presentation is located at [demdk.ipynb](https://github.com/kovashikawa/demdk/blob/main/demdk.ipynb)

---

## short description

your company provides a feature that allows users to schedule recurring allowances, enabling them to set a specific amount and periodicity (`daily`, `weekly`, `biweekly`, or `monthly`) for payments. the backend process responsible for updating the system’s allowance and payment schedule tables encountered issues, leading to discrepancies in the `next_payment_day` fields across datasets.

you are given data reflecting all recorded events and backend table states up to `2024-12-03`. your task is to analyze the data and report inconsistencies.

available datasets:
![database schema](https://github.com/kovashikawa/demdk/blob/main/images/modak_db.png?raw=true)

### task

using the `allowance_events` dataset as the source of truth, analyze the data and identify inconsistencies in `next_payment_day` and `payment_date`. create a detailed report describing:
* discrepancies in the backend tables
* patterns in the errors
* potential causes and scope of the problem

---

## findings

you can see the main findings at the [demdk.ipynb](https://github.com/kovashikawa/demdk/blob/main/demdk.ipynb). includes visualizations and a data-driven analysis explaining where the errors are concentrated, as well as potential bugs outside the scope of this exercise.

in summary, we can say that most of the errors were found in the `biweekly` and `weekly` frequencies. this means that it is almost certain that we will find bugs in the backend code that made these updates:

![freq_error_plot](https://github.com/kovashikawa/demdk/blob/main/images/freq_error.png?raw=true)

it is worth mentioning that:

* most inconsistencies were found in the `biweekly` and `weekly` payment frequencies, suggesting that the backend logic handling these updates may contain bugs
* errors in the `daily` frequency mostly resulted from the table not being updated on `CURRENT_DATE = 2024-12-03`
* the single observed `monthly` error was due to incorrect event log relations rather than the main issue affecting other frequencies (as discussed in the notebook).

for the logic of this code I made the following assumption: the `biweekly` frequency is expected to trigger payments on the 1st and 3rd week of each month

---

## structure of this repository

```
📂 Project Root
├── 📂 data                 # Contains the dataset files
│
├── 📂 images               # Stores saved plots and figures
│
├── 📂 utils                # Utility scripts for data processing
│
├── 📜 LICENSE              # Project license
├── 📜 README.md            # Project documentation
├── 📜 data-challenge.pdf   # Challenge description 
│
├── 📓 demdk.ipynb          # Jupyter Notebook for data analysis 
├── 📓 draft_exploratory_data_analysis.ipynb  # Exploratory analysis notebook
│
└── 📜 requirements.txt     # Dependencies and setup
```

---

## how to run locally?

to run the analysis locally, follow these steps:

1. clone the repository

```bash
git clone https://github.com/kovashikawa/demdk.git
cd demdk
```

2. create a venv

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

3. install dependencies

make sure you have python 3 installed, then install the required packages:

```bash
pip install -r requirements.txt
```

4. run jupyter:

call it and open `demdk.ipynb`:

```bash
jupyter notebook
```

navigate to `demdk.ipynb` and execute
