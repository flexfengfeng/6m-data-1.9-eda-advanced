# 📝 Assignment: EDA Advanced — The Q3 Review Pack

> ⏱️ **Estimated Time:** 65–80 minutes | Complete this **after** your class session.

---

## 🎯 Learning Objectives Revisited

This assignment reinforces what you practised in class:

- Parsing dates, resampling to a different grain, and smoothing with rolling windows
- Merging on one key and on two, and choosing the right `how`
- Reshaping wide ↔ long so two tables can be compared
- Building summary tables with `groupby`, `pivot_table` and `crosstab`

**The four beats apply to every task below:** *Question → Grain → Aggregation → Check.*
Write the grain down before you write the code. It will save you more time than it costs.

---

## Part 1: Conceptual Check (15 min)

**Question 1:** You merge 6,840 sales rows with a 5-row outlet lookup table using
`how="left"`, and the result has **7,200** rows. Nothing errored. What happened, and which one
argument would have turned this into a loud failure instead of a silent one?

**Question 2:** `df.resample("M").sum()` and `df.resample("M").mean()` on the same daily revenue give
you two different pictures of February. Which one would you show a manager who asked "how did
February go?", and what would you say alongside it?

**Question 3:** You have monthly revenue with one column per month (wide), and monthly targets with a
`month` column (long). Write the one line that makes them joinable, and say which of the two you
would reshape.

**Question 4:** `pd.crosstab(df["a"], df["b"])` and
`df.pivot_table(index="a", columns="b", values="c", aggfunc="count")` can produce the same table.
When would you deliberately reach for `crosstab` instead?

**Question 5:** Two outlets have monthly revenues correlated at **−0.72**. Your colleague concludes
that one is stealing customers from the other. Give two other explanations that fit the same number
equally well, and say what you would check first.

<details>
<summary>💡 Check Your Answers</summary>

**Q1:** The lookup table has **duplicate `outlet_id` values**. A left join matches every left row
against *every* matching right row, so one duplicate in the lookup silently multiplies those sales
rows — and inflates every total built from them. `validate="many_to_one"` would have raised
`MergeError` instead. `right["outlet_id"].duplicated().sum()` finds it directly. This is the most
expensive silent bug in this lesson: it makes numbers *bigger*, and nobody questions a bigger number.

**Q2:** Show the **mean** (average trading day) and mention the total. February's total falls every
year because it has 28 days instead of 31, and often a public holiday too. The total answers "how
much money came in", which is a valid question; but "how did February go" is about performance, and
performance per trading day is what is comparable. Best practice: show both, and say which one you
are drawing the conclusion from.

**Q3:** `targets = targets_wide.melt(id_vars="outlet_id", var_name="month", value_name="target_sgd")`
— reshape the **wide** one. Long format is the joinable format: a key has to exist as a column, and
in the wide layout "month" only exists as a set of headers. General habit: melt to compute, pivot to
present.

**Q4:** When you are counting **occurrences of combinations** and there is no value column to
aggregate. `crosstab` takes two Series directly, defaults to counting, and has `normalize=` built in
for row/column percentages. `pivot_table` needs a DataFrame and a `values` column. Same engine
underneath; `crosstab` is the version shaped for frequency questions.

**Q5:** Three explanations fit equally well: (a) **coincidence of timeline** — one is declining and
the other growing over the same period for unrelated reasons; (b) a **common cause** — an area
redevelopment, a bus route change, a competitor opening near one of them; (c) **too few data points**
— with 18 monthly values, a strong correlation is not hard to get by chance. Check first: plot both
series and look at *when* each one moved. If one changed on a specific date and the other drifted
throughout, cannibalisation is very unlikely. Then check whether they even share customers — 8 km
apart with different catchments makes the story implausible on its face.

</details>

---

## Part 2: Practical Challenge (45–60 min)

### Scenario: "The Q3 Review Pack"

Your Lesson 1.9 analysis landed well. The owner has now asked for a short pack ahead of the Q3
review, with four specific questions. Same data, new questions.

Start a new notebook in `notebooks/` and set up:

```python
import pandas as pd
import numpy as np

sales = pd.read_csv("../data/daily_sales.csv", parse_dates=["date"])
outlets = pd.read_csv("../data/outlets.csv", parse_dates=["opened_date"])
roster = pd.read_csv("../data/roster.csv", parse_dates=["week_start"])
targets_wide = pd.read_csv("../data/targets_wide.csv")
```

---

### Challenge 1: "Is Tampines Mall as steady as it looks?" (Time)

Tampines Mall (`OUT-02`) has been flat all year, which everyone has read as "stable".

**Tasks:**
1. Build a **weekly** revenue series for `OUT-02` (weeks starting Monday).
2. Add a **4-week rolling mean** column beside it.
3. Report its best and worst weeks by revenue.
4. In one sentence: is "stable" the right word, or is it "noisy around a flat average"? Which
   column did you use to decide, and why?

<details>
<summary>💡 Hint</summary>

Filter to the outlet first, then `.groupby(pd.Grouper(key="date", freq="W-MON", label="left"))`, or
`set_index("date")` and use `.resample("W-MON")`. `.idxmax()` and `.idxmin()` give you the *labels*
of the best and worst weeks; `.max()` and `.min()` give the values.

</details>

<details>
<summary>✅ Solution</summary>

```python
# Beat 2: the grain is one row per week, for one outlet.
t = sales[sales["outlet_id"] == "OUT-02"]
weekly = t.groupby(pd.Grouper(key="date", freq="W-MON", label="left"))["revenue_sgd"].sum()

# Drop the two partial weeks at the ends -- they are not comparable to full weeks.
weekly = weekly.iloc[1:-1]

view = pd.DataFrame({
    "revenue": weekly.round(0),
    "rolling_4w": weekly.rolling(4).mean().round(0),
})

print(view.tail(8))
print("\nbest week: ", weekly.idxmax().date(), f"${weekly.max():,.0f}")
print("worst week:", weekly.idxmin().date(), f"${weekly.min():,.0f}")
print(f"\nspread: best is {weekly.max() / weekly.min() - 1:.0%} above worst")
```

**What to notice:** the raw weekly column swings by roughly a quarter between the best and worst weeks,
while the 4-week rolling column barely moves. So "stable" is right *at the level of a month* and
wrong at the level of a week. The rolling column is the one to base a judgement on; the raw column is
the one to look at if you are scheduling staff, because that swing is real and someone has to be
rostered for it.

</details>

---

### Challenge 2: "Are we paying for staff we do not need?" (Joins)

**Tasks:**
1. Build weekly revenue per outlet (one row per outlet per week, weeks starting Monday).
2. Merge it with `roster` on **both** keys, and prove the merge did not lose or duplicate rows.
3. Add a `rev_per_staff_hour` column.
4. Find the **10 worst weeks** by `rev_per_staff_hour` across the whole chain. Which outlet dominates
   that list, and when do those weeks cluster?

<details>
<summary>💡 Hint</summary>

`validate="one_to_one"` on the merge does the proving for you — it raises if either side has a
duplicate key pair. Also compare row counts before and after, and use `how="inner"` deliberately
here: a week with no roster row cannot produce an efficiency number at all.

</details>

<details>
<summary>✅ Solution</summary>

```python
weekly_sales = (
    sales.groupby(["outlet_id", pd.Grouper(key="date", freq="W-MON", label="left")])["revenue_sgd"]
    .sum()
    .reset_index()
    .rename(columns={"date": "week_start"})
)

staffed = weekly_sales.merge(
    roster, on=["outlet_id", "week_start"], how="inner", validate="one_to_one"
)

print(f"sales weeks: {len(weekly_sales)}  roster weeks: {len(roster)}  matched: {len(staffed)}")

staffed["rev_per_staff_hour"] = (staffed["revenue_sgd"] / staffed["staff_hours"]).round(2)

worst = staffed.nsmallest(10, "rev_per_staff_hour")
print(worst[["outlet_id", "week_start", "revenue_sgd", "staff_hours", "rev_per_staff_hour"]])
print("\noutlet counts in the worst 10:")
print(worst["outlet_id"].value_counts())
```

**What to notice:** `OUT-03` (Marina Bay) dominates the list, and every one of those weeks falls **after early November 2024** —
after the competitor opened, spread across the eight months since. Revenue stepped down; the roster did not. Note that
the merge is deliberately `inner` here and you can justify it: a week with no roster row has no
denominator, so it cannot appear in an efficiency table at all. That is the standard for choosing
`inner` — you can say why losing the row is correct.

</details>

---

### Challenge 3: "Who is actually hitting target?" (Reshape + aggregate)

**Tasks:**
1. `melt` `targets_wide` into long format.
2. Build monthly actual revenue per outlet, and join the targets on.
3. Add a boolean `hit_target` column.
4. Produce a table with **one row per outlet** showing months hit, months missed, and hit rate as a
   percentage. Sort it worst-first.
5. One sentence: does the hit rate tell the same story as the revenue trend from class? If not, why not?

<details>
<summary>💡 Hint</summary>

Both sides of a join must be the same type. Your actuals will have a `Period` month; the melted
targets have text like `"2024-01"`. `.astype(str)` on the Period side is the easy fix. A boolean
column's `.mean()` is its proportion of `True` — which is exactly a hit rate.

</details>

<details>
<summary>✅ Solution</summary>

```python
targets = targets_wide.melt(id_vars="outlet_id", var_name="month", value_name="target_sgd")

actual = (
    sales.groupby(["outlet_id", sales["date"].dt.to_period("M").astype(str)])["revenue_sgd"]
    .sum()
    .reset_index()
)
actual.columns = ["outlet_id", "month", "revenue_sgd"]

perf = actual.merge(targets, on=["outlet_id", "month"], how="left")
perf["hit_target"] = perf["revenue_sgd"] >= perf["target_sgd"]

summary = perf.dropna(subset=["target_sgd"]).groupby("outlet_id").agg(
    months=("hit_target", "size"),
    hit=("hit_target", "sum"),
)
summary["missed"] = summary["months"] - summary["hit"]
summary["hit_rate_pct"] = (summary["hit"] / summary["months"] * 100).round(1)

print(summary.sort_values("hit_rate_pct"))
```

**What to notice — and this is the interesting part.** Marina Bay and Raffles Place have the **same
hit rate**: 5 of 18 months each, 27.8%. One of them fell 28% year on year and the other fell 1.5%. The
hit rate cannot tell them apart at all.

Why? The targets were set once, from an early-2024 run rate with flat growth applied to every month.
So Holland Village clears a bar set far too low for it (16 of 18), Raffles Place quietly misses a bar
set slightly too high, and Marina Bay misses every month from September 2024 onward. The hit rate is
measuring **how good the target was**, at least as much as how the outlet performed.

Two lessons in that. First, a cumulative measure hides *when* things changed: nothing in this table
points at November 2024, which is the single most important fact about Marina Bay. Second, always ask
where a target came from before you report performance against it. "Missed target 13 months out of
18" and "revenue stepped down 21% in one week last November" are both true, and only one of them
tells the owner what to do.

Also note `dropna(subset=["target_sgd"])`: the pop-up kiosk has no target, so it cannot have a hit
rate. Dropping it here is defensible; silently counting it as a miss would not be.


</details>

---

### Challenge 4: "What exactly did Marina Bay lose?" (Aggregate)

Revenue fell 34%. But *which trade* fell — the morning commuters, the lunch crowd, or the evening?

**Tasks:**
1. Filter to `OUT-03` and split the data into two windows: 2024 H1 and 2025 H1.
2. For each window, build the revenue mix by `daypart` **as a percentage of that window's total**.
3. Put the two side by side and compute the change in percentage points.
4. Then do it again in **dollars per day** rather than percentages.
5. One sentence: which of the two tables would you put in the pack, and why? (They do not tell the
   same story.)

<details>
<summary>💡 Hint</summary>

Percentages of a shrinking total are treacherous: a daypart can *grow* as a share while *falling* in
dollars, simply because everything else fell faster. This is why task 4 exists.

</details>

<details>
<summary>✅ Solution</summary>

```python
marina = sales[sales["outlet_id"] == "OUT-03"]

h1_2024 = marina[(marina["date"] >= "2024-01-01") & (marina["date"] <= "2024-06-30")]
h1_2025 = marina[(marina["date"] >= "2025-01-01") & (marina["date"] <= "2025-06-30")]

def mix_pct(df):
    by_part = df.groupby("daypart")["revenue_sgd"].sum()
    return (by_part / by_part.sum() * 100).round(1)

def per_day(df):
    by_part = df.groupby("daypart")["revenue_sgd"].sum()
    return (by_part / df["date"].nunique()).round(0)

order = ["Morning", "Midday", "Evening"]

share = pd.DataFrame({"2024_h1_pct": mix_pct(h1_2024), "2025_h1_pct": mix_pct(h1_2025)}).loc[order]
share["change_pp"] = (share["2025_h1_pct"] - share["2024_h1_pct"]).round(1)
print(share)

dollars = pd.DataFrame({"2024_h1_per_day": per_day(h1_2024), "2025_h1_per_day": per_day(h1_2025)}).loc[order]
dollars["change_pct"] = ((dollars["2025_h1_per_day"] / dollars["2024_h1_per_day"] - 1) * 100).round(1)
print("\n", dollars)
```

**What to notice:** the percentage-mix table barely moves — every daypart fell by a similar
proportion, so the *shape* of the business is unchanged. The dollars-per-day table shows every
daypart down by roughly the same 27–29%. Put the **dollars** table in the pack: it answers "what did we
lose". The percentage table answers a different and still useful question — "did we lose a particular
kind of customer?" — and the answer is no, which itself rules out a whole class of explanation. A
uniform fall across all three dayparts looks like a general loss of footfall (a competitor taking a
slice of everything), not the loss of one specific customer group.

</details>

---

### 🏆 Stretch Challenge (optional)

The competitor opened on **4 November 2024**. Did it hurt every day of the week equally, or is the
damage concentrated?

Build a table with `weekday` down the side and two columns — average daily revenue for the 8 weeks
*before* and the 8 weeks *after* — plus the percentage change. Then say what you would do with the
answer.

<details>
<summary>✅ Solution</summary>

```python
marina = sales[sales["outlet_id"] == "OUT-03"].copy()
marina["weekday"] = marina["date"].dt.day_name()

# One row per day first, or you will be averaging dayparts instead of days.
daily = marina.groupby(["date", "weekday"])["revenue_sgd"].sum().reset_index()

before = daily[(daily["date"] >= "2024-09-09") & (daily["date"] < "2024-11-04")]
after = daily[(daily["date"] >= "2024-11-04") & (daily["date"] < "2024-12-30")]

order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

cmp = pd.DataFrame({
    "before": before.groupby("weekday")["revenue_sgd"].mean().round(0),
    "after": after.groupby("weekday")["revenue_sgd"].mean().round(0),
}).loc[order]
cmp["change_pct"] = ((cmp["after"] / cmp["before"] - 1) * 100).round(1)

print(cmp)
```

**Watch the grain.** The `groupby(["date", "weekday"])` step is not decoration: without it you would
average *daypart rows*, not days, and every number would be roughly a third of the truth. The ratios
would survive but the levels would be nonsense — the kind of error that passes review because the
percentages still look plausible.

**What you should see:** every day of the week is down, by roughly 18–26%, with midweek worst and
Saturday least affected. There is no single day carrying the damage.

**What to do with it — and what not to.** A concentrated fall on weekdays would say "the competitor
is taking commuters" and point you at the morning offer; a weekend-only fall would point at
destination visitors instead. A fall spread evenly across the whole week says neither, and that is
still a finding: it is consistent with a general loss of footfall rather than the loss of one
customer group. Be careful with the day-by-day percentages, though — each one comes from only eight
observations, so the gap between Tuesday's −26% and Monday's −18% is well inside the noise. Read the
pattern, not the ranking.

</details>

---

## 💬 Reflection (5 min)

In 2–3 sentences:

> In class, the inner join silently removed $61,310 from the chain total. You would not have noticed
> if the notebook had not printed both numbers side by side. What will you *actually do* differently
> — a specific habit, in code — to catch that in your own work? Be concrete enough that you could
> write it as a checklist item.

---

## 📤 Share Your Work

Post your Challenge 2 table (the 10 worst weeks) and your reflection in the **#peer-reviews** Discord
channel. For questions, post in **#questions**.
