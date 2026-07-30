# 📚 Lesson 1.9: EDA Advanced — Data Wrangling & Analysis

**Theme:** The Diagnosis — clean rows answer nothing until you group them

---

## 📅 Lesson Overview

**Total: 180 minutes**, including 2 × 10-minute breaks and one group exercise per section.

| Section | Duration | Topic / Activity |
|---------|----------|-----------------|
| Setup | 5 min | Imports, load `data/daily_sales.csv`, the "why this matters" hook |
| **Part 1: Time Series** | 45 min | `to_datetime`, DatetimeIndex, `.resample()`, `.rolling()`, `.shift()` *(incl. 10-min Group Exercise 1)* |
| ☕ Break | 10 min | |
| **Part 2: Data Integration** | 45 min | `merge` (inner/left/right/outer), `melt`, `pivot` *(incl. 12-min Group Exercise 2)* |
| ☕ Break | 10 min | |
| **Part 3: Aggregation & Reporting** | 45 min | `groupby` split-apply-combine, `.agg()`, `pivot_table`, `crosstab` *(incl. 10-min Group Exercise 3)* |
| **Part 4: From Table to Decision** | 20 min | Assemble the one-slide answer; hand off to Lesson 1.10 |

**One business problem, start to finish.**

> **The Daily Grind** is a four-outlet café chain in Singapore. Chain revenue has been flat for two
> quarters and the owner must decide, this month, whether to renew the Marina Bay lease. You have
> 18 months of daily sales, a staff roster, an outlet reference table, and a target sheet.
> Everything in this session works on that one problem.

The chain total *is* flat — and that is the trap. Marina Bay is falling and Holland Village is
rising by almost exactly the same amount, so the two cancel out in the headline number. No amount
of cleaning reveals this. Only grouping does. That is what this lesson is for.

---

## 🎯 Learning Objectives

By the end of this lesson, you will be able to:

1. **Parse** and manipulate datetime data to perform time-based resampling and rolling window calculations.
2. **Merge** multiple DataFrames using SQL-style joins and convert between wide and long data formats.
3. **Aggregate** data using `groupby`, pivot tables, and cross-tabulations to generate summary reports.
4. **Apply** the split-apply-combine pattern to answer complex analytical questions on real datasets.

---

## 🧭 The habit this lesson teaches

Lesson 1.8 gave you four beats for every fix: **find it → decide → apply → verify.**
Lesson 1.9 has its own four beats, and every summary in the notebook follows them:

| Beat | Question | Example |
|---|---|---|
| **1. Question** | What decision does this number serve? | "Should we renew the Marina Bay lease?" |
| **2. Grain** | One row per *what*? | One row per outlet, per month |
| **3. Aggregation** | Sum, mean, count — and why that one? | Sum revenue (totals matter); mean revenue per staff hour (efficiency matters) |
| **4. Check** | Does the total still tie back? | Grouped total = ungrouped total, or you lost rows somewhere |

Beat 4 is the one people skip, and it is the one that catches the mistake in Part 2, where a join
silently deletes $61,310 of revenue.

---

## 📂 Course Materials

| Material | Description | Est. Time |
|----------|-------------|-----------|
| [Pre-Class](./pre-class.md) | Datetime as a type; wide vs long; joins; split-apply-combine; correlation vs covariance | 30–40 min |
| [Lesson Plan](./lesson.md) | Instructor guide: agenda, timings, teaching notes | 180 min |
| [Assignment](./assignment.md) | The Q3 review pack — build the tables that answer the owner's questions | 60–75 min |
| [Reference](./reference.md) | Wrangling cheat sheet; offset aliases; join decision table; deep dives moved out of the notebook | As needed |

---

## 🗂️ The Data

All five files live in `data/` and are produced by `data/make_cafe_data.py` (synthetic, reproducible).

| File | Rows | Grain | Used for |
|---|---|---|---|
| `daily_sales.csv` | 6,840 | one row per outlet, per day, per daypart | the spine: time series, grouping, pivots |
| `outlets.csv` | 5 | one row per outlet | the merge key — name, region, seats, rent |
| `roster.csv` | 325 | one row per outlet, per week | merging on two keys; revenue per staff hour |
| `targets_wide.csv` | 4 × 19 | one row per outlet, one **column per month** | `melt` — wide → long before you can join it |
| `tickets_week.csv` | 4,916 | one row per till receipt (one week only) | `crosstab`, distributions, per-ticket questions |

`tips.csv` and the two `yahoo_*.pkl` files are left over from the earlier version of this lesson. Nothing in the notebook,
assignment or reference uses them, and you can delete them.

Two deliberate traps live in this data. Both are teaching moments, not bugs:

- `daily_sales.csv` contains **OUT-05**, a pop-up kiosk that is *not* in `outlets.csv`.
- `outlets.csv` contains **OUT-06** (Sentosa Cove), which has *not opened* and has no sales.

An inner join quietly loses the kiosk's revenue. A left join keeps it with a blank name. An outer
join shows you both problems at once. Which one is "right" depends on the question — that is the point.

---

## 🛠️ Tools & Setup

- **[VS Code](https://code.visualstudio.com)** + Python + Jupyter extensions *(recommended)*.
- **[Google Colab](https://colab.research.google.com)** *(alternative)*.
- **Notebook:** `notebooks/eda_advanced.ipynb` — select the `pds` kernel in VS Code.
- **Environment:** `conda env create -f environment.yml` then `conda activate pds`.
- **Pandas version:** the notebook targets the `pds` environment (pandas 1.5) and avoids APIs
  changed in pandas 2.x, so it also runs unmodified on Google Colab.
- **Regenerate the data** (optional): `python data/make_cafe_data.py`.

---

## ➡️ Where this sits

| Lesson | The question it answers |
|---|---|
| 1.8 EDA Basic | **Can I trust this data?** — missing values, duplicates, impossible values |
| **1.9 EDA Advanced** | **What is the pattern?** — time, joins, reshaping, grouping |
| 1.10 Visualisation | **How do I make them act?** — chart choice, design, story |

The summary tables you build in Part 4 are the exact tables Lesson 1.10 turns into the owner's one
slide. Keep your notebook.
