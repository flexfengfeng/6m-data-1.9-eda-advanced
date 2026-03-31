# 🎓 Lesson 1.9: EDA Advanced — Instructor Guide

## Session Overview

| Item | Detail |
|------|--------|
| **Duration** | 3 hours |
| **Format** | Flipped Classroom + Guided Coding in Jupyter |
| **Prerequisites** | EDA Basic (Lesson 1.8); covariance vs. correlation; datetime basics (pre-class) |
| **Tools** | VS Code + `pds` conda environment; or Google Colab |
| **Notebook** | `notebooks/eda_advanced.ipynb` |

### Agenda

| Time | Section | Focus |
|------|---------|-------|
| 0:00 – 0:10 | Welcome & Pre-Class Review | Concept check; resolve setup issues |
| 0:10 – 1:00 | Part 1: Time Series Analysis | Datetime; resampling; rolling windows |
| 1:00 – 1:05 | Break | — |
| 1:05 – 1:55 | Part 2: Data Integration | Merges, joins, melt & pivot |
| 1:55 – 2:00 | Break | — |
| 2:00 – 2:55 | Part 3: Aggregation & Reporting | GroupBy; pivot tables; cross-tabs |
| 2:55 – 3:00 | Wrap-Up | Takeaways & mini-project briefing |

> **Instructor Note:** This lesson uses a financial dataset (price/volume) and the restaurant tips dataset. Both are in the `data/` folder. Have students confirm they can load both before starting Part 1.

---

## 🏃 Part 1: Time Series Analysis (50 min)

### 🎯 Learning Objective
Parse datetime data and use resampling and rolling windows to surface time-based trends.

### 📖 Theory Recap (10 min)

**Analogy:** Treating a date as text is like trying to add "Monday" + "Tuesday" — it makes no sense. Converting to a datetime object turns a label into a number line you can do maths on.

Key concepts:
- **Parsing:** `pd.to_datetime()` converts strings to datetime objects.
- **Indexing:** Set the datetime column as the index with `.set_index()` to unlock time-based operations.
- **Resampling:** `df.resample('M').sum()` — collapses daily data into monthly totals.
- **Rolling windows:** `df['col'].rolling(7).mean()` — smooths data over a moving window.

```python
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')
monthly = df['price'].resample('M').mean()
rolling_avg = df['price'].rolling(window=30).mean()
```

### 🛠️ Hands-On Activity: "The Market Monitor" (30 min)

**Scenario:** You're an analyst at an investment firm. You've received daily stock price data and need to summarise it for a monthly board report.

**In the notebook, work through:**
1. Load the financial dataset and convert the date column to datetime.
2. Set the date as the index and check `.index.dtype` — confirm it's `datetime64`.
3. Resample to monthly frequency using `'M'` — compute both `mean` and `sum`.
4. Add a 30-day rolling average column and plot it alongside the raw daily prices.

**Discussion Questions:**
- "What does a flat rolling average during a volatile period tell you?"
- "Why would you use `resample('W')` vs. `resample('M')` for different business questions?"

### 💬 Q&A & Reflection (10 min)

- **Common Misconception:** "I can just sort by the date string." → String sorting gives '2023-09-01' > '2023-10-01' alphabetically but not chronologically. Always convert first.
- **Business Case:** Netflix uses 7-day rolling averages on viewing data to distinguish genuine trend shifts from weekend spikes when making content investment decisions.

---

## 🏃 Part 2: Data Integration (50 min)

### 🎯 Learning Objective
Combine DataFrames using SQL-style merges and reshape data between wide and long formats.

### 📖 Theory Recap (10 min)

**Analogy:** Merging is like a JOIN in SQL — you're stitching two tables together on a shared key. Reshaping (melt/pivot) is like rotating a spreadsheet — the same data, different orientation.

| Operation | Pandas Method | SQL Equivalent |
|-----------|---------------|----------------|
| Keep all left rows | `pd.merge(how='left')` | LEFT JOIN |
| Keep matching only | `pd.merge(how='inner')` | INNER JOIN |
| Wide → Long | `pd.melt()` | UNPIVOT |
| Long → Wide | `df.pivot()` / `df.pivot_table()` | PIVOT |

**When to use long format:** For plotting with Seaborn, groupby operations, and statistical modelling.
**When to use wide format:** For human-readable reports and Excel export.

### 🛠️ Hands-On Activity: "The Data Integration Pipeline" (30 min)

**Scenario:** You have two separate datasets — one with customer transactions, one with customer demographics. You need to combine them and reshape the result for reporting.

**In the notebook, work through:**

1. Perform a left merge between two DataFrames on a common key:

```python
merged = pd.merge(transactions, customers, on='customer_id', how='left')
```

2. Check for NaN values introduced by the merge — what does a NaN indicate after a left join?
3. Use `pd.melt()` to convert a wide sales DataFrame into long format:

```python
long_df = pd.melt(wide_df, id_vars=['region'], var_name='month', value_name='sales')
```

4. Pivot it back to wide format with `.pivot()` — confirm the result matches the original.

**Discussion Questions:**
- "What happens to rows in a left join when there's no matching key on the right side?"
- "Why do tools like Seaborn prefer long format data?"

### 💬 Q&A & Reflection (10 min)

- **Common Misconception:** "Pivot and melt are opposites, so using one then the other always gets you back to the start." → Only true if there are no aggregations. `pivot_table()` aggregates, so information can be lost.
- **Business Case:** Retail chains like IKEA use wide-to-long reshaping to consolidate regional sales reports from different country formats into a single analytical database.

---

## 🏃 Part 3: Aggregation & Reporting (50 min)

### 🎯 Learning Objective
Generate business-ready summaries using GroupBy, pivot tables, and cross-tabulations.

### 📖 Theory Recap (10 min)

**Analogy:** The split-apply-combine pattern is like sorting exam papers by class, marking each class separately, then compiling the class averages on one sheet. Split → Apply → Combine.

Key tools:
- **`groupby()`:** Most flexible aggregation. `df.groupby('category')['value'].agg(['mean', 'sum', 'count'])`
- **`pivot_table()`:** Multi-dimensional summarisation with automatic aggregation.
- **`pd.crosstab()`:** Frequency counting between two categorical variables — great for understanding distributions.

### 🛠️ Hands-On Activity: "The Executive Summary" (30 min)

**Scenario:** The leadership team needs a weekly report. Your job is to generate three summary tables from the restaurant tips dataset.

**In the notebook, work through:**

1. Use `groupby()` to compute average bill and tip by day and meal time:

```python
summary = tips.groupby(['day', 'time'])[['total_bill', 'tip']].agg(['mean', 'count'])
```

2. Create a pivot table showing average bill by day (rows) and meal time (columns):

```python
pivot = pd.pivot_table(tips, values='total_bill', index='day', columns='time', aggfunc='mean')
```

3. Use `pd.crosstab()` to count combinations of smoker status and meal time:

```python
ct = pd.crosstab(tips['smoker'], tips['time'], margins=True)
```

**Discussion Questions:**
- "From the pivot table, which day + meal combination generates the highest average bill?"
- "What does the `margins=True` parameter in crosstab add, and why is it useful?"

### 💬 Q&A & Reflection (10 min)

- **Common Misconception:** "`groupby()` and `pivot_table()` are different tools." → They often produce identical results; `pivot_table()` is a convenience wrapper around `groupby()` for 2D summarisation.
- **Business Case:** Airbnb's data team uses pivot tables to compare booking rates by city × listing type × season, enabling pricing strategy decisions for millions of listings.

---

## 🎯 Wrap-Up (5 min)

### Key Takeaways
1. **Always convert dates to datetime objects** — string dates break time-based operations.
2. **Merge strategy matters:** left joins preserve your primary table; inner joins give you only matches. Know the difference before choosing.
3. **GroupBy is your reporting engine:** combine with `agg()`, `pivot_table()`, and `crosstab()` to generate executive-ready summaries in seconds.

### Next Steps
- **Post-Class:** Complete the [post-class.md](./post-class.md) — conceptual quiz + mini-project (time series resampling + pivot tables).
- **Next Lesson:** Lesson 1.10 covers Data Visualisation — turning these aggregated insights into compelling charts and stories.
