# demdk - data engineering @ modak
> this repo consists of a technical exercise for the data engineering position at [modak](https://modak.na.teamtailor.com/)

the complete exercise description can be found at the [.pdf](https://github.com/kovashikawa/demdk/blob/main/data-challenge.pdf)

---

## short description

your company provides a feature that allows users to schedule recurring allowances, enabling them to set a specific amount and periodicity (`daily`, `weekly`, `biweekly`, or `monthly`) for payments. the backend process responsible for updating the system’s allowance and payment schedule tables encountered issues, leading to discrepancies in the `next_payment_day` fields across datasets.

you are given data reflecting all recorded events and backend table states up to `2024-12-03`. your task is to analyze the data and report inconsistencies.

available datasets:
![database schema](https://github.com/kovashikawa/demdk/blob/main/modak_db.png?raw=true)

### task

using the `allowance_events` dataset as the source of truth, analyze the data and identify inconsistencies in `next_payment_day` and `payment_date`. create a detailed report describing:
	•	discrepancies in the backend tables
	•	patterns in the errors
	•	potential causes and scope of the problem

---

## findings

you can see the results at the 