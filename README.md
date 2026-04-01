# 📚 Lesson 1.9: EDA Advanced — Data Wrangling & Analysis

**Theme:** From Messy to Meaningful — reshaping, merging, and analysing complex datasets

---

## 📅 Lesson Overview

| Section | Duration | Topic / Activity |
|---------|----------|-----------------|
| **Part 1: Time Series** | 55 min | Datetime objects; frequency resampling; rolling averages |
| **Part 2: Data Integration** | 55 min | SQL-style merges/joins; melt & pivot (wide ↔ long format) |
| **Part 3: Aggregation & Reporting** | 55 min | GroupBy; pivot tables; cross-tabulations |

---

## 🎯 Learning Outcomes

By the end of this lesson, you will be able to:

1. **Parse** and manipulate datetime data to perform time-based resampling and rolling window calculations.
2. **Merge** multiple DataFrames using SQL-style joins and convert between wide and long data formats.
3. **Aggregate** data using `groupby`, pivot tables, and cross-tabulations to generate summary reports.
4. **Apply** the split-apply-combine pattern to answer complex analytical questions on real datasets.

---

## 📂 Course Materials

| Material | Description | Est. Time |
|----------|-------------|-----------|
| [Pre-Class](./pre-class.md) | Correlation vs. covariance; datetime; wide vs. long format | 30–45 min |
| [Lesson Plan](./lesson.md) | Instructor guide for the 3-hour coding session | 3 hours |
| [Assignment](./assignment.md) | Conceptual quiz + mini-project (time series & pivot tables) | 45–60 min |
| [Reference](./reference.md) | Pandas wrangling cheat sheet; datetime reference | As needed |

---

## 🛠️ Tools & Setup

- **[VS Code](https://code.visualstudio.com)** + Python + Jupyter extensions *(recommended)*.
- **[Google Colab](https://colab.research.google.com)** *(alternative)*.
- **Notebook:** `notebooks/eda_advanced.ipynb` — select the `pds` kernel in VS Code.
- **Environment:** `conda env create -f environment.yml` then `conda activate pds`.
- **Dataset:** Located in `data/` folder (financial price/volume data + tips dataset).
