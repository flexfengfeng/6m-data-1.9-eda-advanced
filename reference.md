# Reference — Lesson 1.9

- [Pandas Data Wrangling Cheatsheet](https://www.datacamp.com/cheat-sheet/pandas-cheat-sheet-data-wrangling-in-python)
- [Working with Dates and Times in Python](https://www.datacamp.com/cheat-sheet/working-with-dates-and-times-in-python-cheat-sheet)
- [Descriptive Statistics Cheatsheet](https://www.datacamp.com/cheat-sheet/descriptive-statistics-cheat-sheet)
- [Tidy Data — the original paper](https://vita.had.co.nz/papers/tidy-data.pdf)
- [pandas: Reshaping and pivot tables (official docs)](https://pandas.pydata.org/docs/user_guide/reshaping.html)

---

## 🗺️ The four beats, on one line

**Question → Grain → Aggregation → Check.**
What decision is this for? One row per what? Sum, mean or count, and why? Does the total tie back?

---

## ⏱️ Time cheat sheet

| Task | Code |
|---|---|
| Text → dates | `pd.to_datetime(s)` |
| …with a known layout | `pd.to_datetime(s, format="%d/%m/%Y")` |
| …day-before-month | `pd.to_datetime(s, dayfirst=True)` |
| …on load | `pd.read_csv(f, parse_dates=["date"])` |
| Date parts | `s.dt.year`, `.dt.month`, `.dt.day_name()`, `.dt.dayofweek`, `.dt.quarter` |
| Month/quarter label | `s.dt.to_period("M")`, `s.dt.to_period("Q")` |
| Date → index | `df.set_index("date").sort_index()` |
| Slice a month | `series["2025-06"]` |
| Slice a range | `series.loc["2025-01":"2025-03"]` (both ends included) |
| Make a calendar | `pd.date_range("2025-01-01", periods=30, freq="D")` |
| Business days only | `pd.bdate_range("2025-01-01", "2025-01-31")` |
| Fill in missing days | `series.reindex(pd.date_range(start, end, freq="D"))` |
| Change grain | `series.resample("M").sum()` |
| Moving average | `series.rolling(7).mean()` |
| Compare to previous | `series.shift(1)`, `series.pct_change()` |
| Elapsed time | `df["end"] - df["start"]` → a `Timedelta` |

**Offset aliases:** `D` day · `B` business day · `W` week (Sun) · `W-MON` week starting Monday ·
`M` month end · `MS` month start · `Q` quarter end · `A`/`Y` year end · `H` hour · `T`/`min` minute.

> **Pandas 2.x note.** `M`, `Q`, `A` and `H` still work but warn; the new spellings are `ME`, `QE`,
> `YE`, `h`. The notebook uses the old ones because they work in **both** pandas 1.5 (the `pds`
> environment) and 2.x. On your own machine with pandas 2.x, prefer the new ones.

---

## 🔗 Join cheat sheet

| Task | Code |
|---|---|
| Join on a column | `left.merge(right, on="key", how="left")` |
| Join on differently named columns | `left.merge(right, left_on="a", right_on="b")` |
| Join on two keys | `left.merge(right, on=["outlet_id", "week_start"])` |
| Join on the index | `left.join(right)` — index-based by default |
| Where did each row come from? | `merge(..., indicator=True)` → a `_merge` column |
| Assert the relationship | `merge(..., validate="many_to_one")` |
| Handle duplicate column names | `merge(..., suffixes=("_sales", "_target"))` |
| Stack tables of the same shape | `pd.concat([df1, df2], ignore_index=True)` |
| Stack side by side | `pd.concat([df1, df2], axis=1)` |

### Which `how`?

| `how` | Keeps | Choose it when |
|---|---|---|
| `inner` | keys in **both** | every output row must have complete attributes |
| `left` | all of the **left** | the left table is your spine and must not shrink — **the default** |
| `right` | all of the **right** | rarely; usually clearer written as a `left` the other way round |
| `outer` | **everything** | reconciling two lists, when the mismatches are the finding |

**The three checks worth running on every merge:**

```python
before = len(left)
out = left.merge(right, on="key", how="left", validate="many_to_one")

# 1. did the row count change unexpectedly? (a left join must not add rows)
print(len(out) == before)

# 2. any unmatched keys? Check a column that came from the RIGHT table -- after a left join
#    the key itself is never null, so `out["key"].isna()` would always say zero.
print(out["a_column_from_right"].isna().sum())

# 3. beat 4: does the total still tie back?
print(round(out["amount"].sum(), 2) == round(left["amount"].sum(), 2))
```

---

## 🔁 Reshape cheat sheet

| Task | Code |
|---|---|
| Wide → long | `df.melt(id_vars="outlet_id", var_name="month", value_name="revenue")` |
| Long → wide | `df.pivot(index="month", columns="outlet_id", values="revenue")` |
| Long → wide, with aggregation | `df.pivot_table(index=..., columns=..., values=..., aggfunc="sum")` |
| Add totals | `pivot_table(..., margins=True)` |
| Index level → columns | `df.unstack()` |
| Columns → index level | `df.stack()` |
| Row percentages | `df.div(df.sum(axis=1), axis=0) * 100` |
| Column percentages | `df.div(df.sum(axis=0), axis=1) * 100` |

`pivot` vs `pivot_table`: `pivot` fails if two rows would land in the same cell; `pivot_table`
aggregates them, because you told it how. That is the only real difference.

---

## 📊 Aggregation cheat sheet

| Task | Code |
|---|---|
| One key | `df.groupby("outlet_id")["revenue"].sum()` |
| Two keys | `df.groupby(["outlet_id", "daypart"])["revenue"].sum()` |
| Keep NaN groups | `df.groupby("region", dropna=False)` |
| Named outputs | `df.groupby("k").agg(total=("revenue", "sum"), n=("revenue", "size"))` |
| Several functions | `df.groupby("k")["revenue"].agg(["sum", "mean", "max"])` |
| Custom function | `df.groupby("k")["revenue"].agg(lambda s: s.max() - s.min())` |
| Resample inside a groupby | `df.groupby(["k", pd.Grouper(key="date", freq="M")])` |
| Group share of total | `df.groupby("k")["revenue"].transform("sum")` |
| Counting combinations | `pd.crosstab(df["a"], df["b"])` |
| …as percentages | `pd.crosstab(df["a"], df["b"], normalize="columns")` |
| …aggregating a value | `pd.crosstab(df["a"], df["b"], values=df["v"], aggfunc="mean")` |

**`count` vs `size` vs `nunique`:** `count` counts non-null values; `size` counts rows including
nulls; `nunique` counts distinct values. Mixing these up is the most common cause of a summary table
that is subtly, confidently wrong.

**`agg` vs `transform` vs `apply`:** `agg` returns one row per group; `transform` returns one value
per *original* row (useful for shares and percentages); `apply` is the flexible, slow last resort.

---

## 📦 Moved out of the lesson notebook

Everything below is correct and useful — it was moved here to keep the 180-minute session on the four
learning outcomes. Copy any block into a notebook cell. Blocks assume:

```python
import pandas as pd
import numpy as np

sales = pd.read_csv("../data/daily_sales.csv", parse_dates=["date"])
outlets = pd.read_csv("../data/outlets.csv", parse_dates=["opened_date"])
chain_daily = sales.groupby("date")["revenue_sgd"].sum()
```

### Hierarchical (Multi-) indexes

A MultiIndex is an index with more than one level. `groupby` on two keys produces one automatically.

```python
# Two levels: outlet, then month.
multi = sales.groupby(["outlet_id", sales["date"].dt.to_period("M")])["revenue_sgd"].sum()
multi.index.names = ["outlet_id", "month"]

multi.head()
```

```python
# Pick one outlet from the outer level.
multi.loc["OUT-03"].head()
```

```python
# `.xs()` takes a cross-section from ANY level -- here, one month across all outlets.
multi.xs(pd.Period("2025-06", freq="M"), level="month")
```

```python
# Swap the levels, then re-sort (a MultiIndex must be sorted to slice efficiently).
multi.swaplevel().sort_index().head()
```

```python
# `.unstack()` promotes the innermost level to columns; `.stack()` is the reverse.
wide = multi.unstack()
print(wide.shape)

wide.stack().head()
```

### `concat` vs `merge`

`merge` joins **sideways** on a key. `concat` stacks tables that already share a shape.

```python
h1 = sales[sales["date"] < "2024-07-01"]
h2 = sales[sales["date"] >= "2024-07-01"]

# Stack them back into one table. `ignore_index=True` renumbers the rows from 0.
stacked = pd.concat([h1, h2], ignore_index=True)

print(len(sales), len(stacked), len(sales) == len(stacked))
```

```python
# `keys=` labels where each piece came from -- it becomes an extra index level.
labelled = pd.concat([h1, h2], keys=["H1", "H2"])
labelled.index.names = ["half", "row"]

labelled.head(2)
```

### `join` vs `merge`

`join` is a convenience wrapper that works on the **index** by default.

```python
lookup = outlets.set_index("outlet_id")[["outlet_name", "region"]]
totals = sales.groupby("outlet_id")[["revenue_sgd"]].sum()

# Both sides are indexed by outlet_id, so `join` needs no arguments.
totals.join(lookup).round(0)
```

```python
# The same thing with merge, being explicit about it.
totals.merge(lookup, left_index=True, right_index=True, how="left").round(0)
```

### `resample().agg()` and `rolling().agg()`

```python
# Several statistics per month, in one pass.
chain_daily.resample("M").agg(["sum", "mean", "min", "max"]).round(0).tail(4)
```

```python
# A rolling window can take several statistics too.
chain_daily.rolling(7).agg(["mean", "std"]).round(0).tail(3)
```

```python
# Centre the window on each day instead of trailing behind it. Better for looking back at
# history; useless for anything live, because it needs days that have not happened yet.
pd.DataFrame({
    "trailing": chain_daily.rolling(7).mean(),
    "centred": chain_daily.rolling(7, center=True).mean(),
}).round(0).loc["2025-06-01":"2025-06-05"]
```

```python
# `expanding()` grows the window from the start -- a running, cumulative average.
chain_daily.expanding().mean().round(0).tail(3)
```

### Upsampling: creating rows that did not exist

```python
weekly = chain_daily.resample("W").sum()

# `asfreq` leaves the new rows empty; `ffill` carries the last known value forward.
pd.DataFrame({
    "asfreq": weekly.resample("D").asfreq(),
    "ffill": weekly.resample("D").ffill(),
}).head(9)
```

> Which is honest depends on what the number *is*. Carrying a weekly **total** forward to every day
> invents revenue. Carrying a **price** forward is usually fine. Ask what the value means before you
> choose a fill.

### Time zones and business days

```python
# A naive timestamp has no time zone; `tz_localize` attaches one, `tz_convert` moves it.
naive = pd.Timestamp("2025-06-16 09:00")
sg = naive.tz_localize("Asia/Singapore")

print(sg)
print(sg.tz_convert("Europe/London"))
```

```python
# Business-day arithmetic: skip weekends without writing a loop.
print(pd.bdate_range("2025-06-16", "2025-06-27").size, "business days in that fortnight")
print(pd.Timestamp("2025-06-20") + pd.offsets.BDay(3))   # Friday + 3 business days
```

```python
# Month-end and quarter-end anchors: useful for reporting periods.
d = pd.Timestamp("2025-06-16")

print("month end:  ", d + pd.offsets.MonthEnd(0))
print("next month: ", d + pd.offsets.MonthBegin(1))
print("quarter end:", d + pd.offsets.QuarterEnd(0))
```

### Period vs Timestamp

A `Timestamp` is an instant. A `Period` is a span — a whole month, a whole quarter. Grouping by month
is usually clearer with a Period: "2025-06" is unambiguous, where "2025-06-30" looks like a single day.

```python
p = pd.Period("2025-06", freq="M")

print(p.start_time, "->", p.end_time)
print("as a timestamp:", p.to_timestamp())
print("quarter it sits in:", p.asfreq("Q"))
```

### `transform` — group statistics without collapsing rows

```python
# Each row's share of its own outlet's total revenue, with all 6,840 rows still intact.
sales["outlet_total"] = sales.groupby("outlet_id")["revenue_sgd"].transform("sum")
sales["share_of_outlet_pct"] = (sales["revenue_sgd"] / sales["outlet_total"] * 100).round(3)

sales[["date", "outlet_id", "revenue_sgd", "share_of_outlet_pct"]].head()
```

### `crosstab` with margins and two levels

```python
tickets = pd.read_csv("../data/tickets_week.csv", parse_dates=["txn_datetime"])

pd.crosstab(
    [tickets["outlet_id"], tickets["daypart"]],   # two levels down the side
    tickets["payment_method"],
    margins=True,
).head(8)
```

---

## 🧭 Diagnosing a summary that looks wrong

| Symptom | Likely cause | Check |
|---|---|---|
| Total is smaller than the raw total | an `inner` join dropped unmatched keys | `merge(..., indicator=True)`, then `value_counts()` on `_merge` |
| Total is larger than the raw total | duplicate keys in the lookup table → rows multiplied | `right["key"].duplicated().sum()`, or `validate="many_to_one"` |
| A merge matched nothing | key dtypes differ (text vs date, `int` vs `str`) | compare `left["key"].dtype` with `right["key"].dtype` |
| Counts far too high | wrong grain — several rows per event | `df.groupby(keys).size()`, and use `nunique` not `count` |
| February looks like a disaster | `sum` where you wanted `mean` | compare `resample("M").sum()` with `.mean()` |
| A percentage moves wildly | the denominator changed, not the numerator | plot the denominator on its own |
| A correlation looks decisive | too few points, or a shared timeline | count the points; plot both series |
