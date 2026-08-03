# 📚 Lesson 1.9: EDA Advanced — Data Wrangling & Analysis

## Session Overview

| | |
|---|---|
| **Duration** | 180 minutes (including 2 × 10-min breaks) |
| **Format** | Guided coding in Jupyter, following the notebook |
| **Tools** | VS Code + `pds` conda environment |
| **Notebook** | `notebooks/eda_advanced.ipynb` |
| **Dataset** | `data/daily_sales.csv` + four supporting files — one business problem, start to finish |

## Agenda

| Time | Part | Topic |
|------|------|-------|
| 0:00 – 0:05 | Setup | Imports, load `daily_sales.csv`, the "flat line" hook |
| 0:05 – 0:50 | Part 1 | Time Series — dates as a type, DatetimeIndex, `resample`, `rolling`, `shift` *(incl. 10-min Group Exercise 1)* |
| 0:50 – 1:00 | ☕ | **Break** |
| 1:00 – 1:45 | Part 2 | Data Integration — `merge` and the four `how`s, two-key merges, `melt`, `pivot` *(incl. 12-min Group Exercise 2)* |
| 1:45 – 1:55 | ☕ | **Break** |
| 1:55 – 2:40 | Part 3 | Aggregation — `groupby`, `.agg()`, `pivot_table`, `crosstab`, correlation *(incl. 10-min Group Exercise 3)* |
| 2:40 – 3:00 | Part 4 | From table to decision — assemble the owner's answer, save it for 1.10 |

**The notebook follows the four learning outcomes in order.** Time comes first because the owner's
question is about change; joining comes second because a row means nothing until it knows which
outlet it belongs to; grouping comes third because it needs both.

---

## 🎬 The business problem (do not skip this)

> **The Daily Grind**, a four-outlet café chain. Chain revenue has been flat for two quarters. The
> Marina Bay lease is up for renewal **this month** — $9,600 a month — and the owner has to sign or
> walk. She sends you 18 months of sales and asks: *what is going on?*

The chain total genuinely is flat. Marina Bay is falling and Holland Village is rising by almost
exactly the same amount, so they cancel in the headline. **The flat line was two opposite stories
cancelling out.** Cleaning could never have found that; only grouping does.

The hook cells at the top of the notebook show the flat total, then the same total split by outlet.
Two cells, two minutes, and the rest of the session has a reason to exist. Run them first.

Then write down three things you cannot see yet — the notebook ticks them off as you go:

1. Marina Bay's fall is a **step**, not a slope, dated to one week. *(Part 1)*
2. There is a **fifth outlet** in the sales file that does not exist in the outlet list. *(Part 2)*
3. Marina Bay is still **staffed for the revenue it used to make**. *(Part 3)*

---

## 🧭 The four beats of every summary

Lesson 1.8's habit was *find it → decide → apply → verify*. This lesson's habit is:

**1. Question** → **2. Grain** → **3. Aggregation** → **4. Check**

| Beat | Ask | Why it bites |
|---|---|---|
| Question | What decision does this number serve? | Stops you producing tables nobody uses |
| Grain | One row per *what*? | `sales` has 3 rows per outlet per day; a careless total triples or thirds |
| Aggregation | Sum, mean or count — why that one? | Sum makes February look like a crisis; mean does not |
| Check | Does the total tie back? | Part 2's inner join loses **$61,310** without a single warning |

Say the beats at each summary in Part 3. By Part 4 you should be reaching for them without prompting.

### How to work through the notebook

- **Start with the hook.** Flat chain total, then the per-outlet split. Two minutes, and everything
  after it has a reason to exist.
- **Each section is spine-then-drills.** The spine works on the café data and carries the story; the
  small hand-built tables (`drill`, `clash`, `gappy`) isolate one mechanic. Short on time? Skip
  drills — never the spine.
- **The three payoff moments** are: the step at Marina Bay (1.4), the four-way join comparison (2.1),
  and revenue per staff hour (3.5). Everything else is scaffolding for those.
- **Dwell on the date-format cell in 1.1.** `"03/06/2025"` parsed the wrong way round raises no error
  and shifts your report by three months. It is the same bug people hit in Excel.
- **The group exercises fade on purpose:** (a) is worked or blank-filling, (b) fills blanks, (c) is
  from scratch, (d) is explain-only with no code. Expected outputs are stated, so you can check
  yourself without waiting.
- Deep dives (MultiIndex, `concat` vs `merge`, `stack`/`unstack`, time zones, business days) live in
  `reference.md` — read them after the session, not during.
- Part 4 writes `data/lesson19_decision.csv`. **Lesson 1.10 opens that file** — run the cell.

---

## 🎯 Learning Objectives

By the end of this session, you will be able to:

1. Parse and manipulate datetime data to perform time-based resampling and rolling window calculations.
2. Merge multiple DataFrames using SQL-style joins and convert between wide and long data formats.
3. Aggregate data using `groupby`, pivot tables, and cross-tabulations to generate summary reports.
4. Apply the split-apply-combine pattern to answer complex analytical questions on real datasets.

---

## Before You Start

**Have you completed the pre-class reading?**
- ✓ You know a date is a *type*, not a piece of text
- ✓ You can explain wide vs long format, and which one code prefers
- ✓ You can explain an inner join vs a left join using the party-guest-list analogy
- ✓ You can say the three words of split-apply-combine
- ✓ `pds` conda environment is set up

Open `notebooks/eda_advanced.ipynb` in VS Code and select the `pds` kernel.

---

## 🏃 Part 1: Time Series (45 min)

Follow **Part 1** in the notebook.

**1.1 — a date is a type, not a string.** Text dates sort like words: `"2024-10-02"` comes before
`"2024-9-30"`. `pd.to_datetime` fixes that, and `.dt` then unlocks every date question the way
`.str` unlocked text questions in 1.8.

**1.2 — the DatetimeIndex.** Promote the date to the row label and you get string slicing
(`series["2025-06"]`) and access to `resample` / `rolling`. Also: `reindex` onto a full calendar, so
missing days show as `NaN` instead of vanishing.

**1.3 — `resample` changes the grain of time.**

| Alias | Bucket | | Alias | Bucket |
|---|---|---|---|---|
| `D` | day | | `M` | month end |
| `W` | week | | `Q` | quarter end |

> The `sum` vs `mean` cell is beat 3 made visible. February's *total* drops and its *average day*
> does not — 28 days versus 31, plus Chinese New Year. A manager shown only totals goes hunting for
> a cause that does not exist.

**1.4 — `rolling` smooths the noise.** A 7-day mean cancels the weekday/weekend cycle and leaves the
trend. This is what separates a **step** (something happened on a date) from a **slope** (something
is slowly changing). Marina Bay's average day falls 21% either side of 4 November 2024 — a step.
A competitor opened next door.

**1.5 — the payoff.** The same `resample`, done per outlet, shows the divergence the chain total hid.
Then the beat-4 check: per-outlet totals must tie back to the raw total.

---

## 🏃 Part 2: Data Integration (45 min)

Continue with **Part 2**.

**2.1 — `merge` and the four `how`s.** The key is `outlet_id`. The comparison cell prints row count
*and* revenue total for `inner`, `left`, `right`, `outer`.

| `how` | Keeps | Use when |
|---|---|---|
| `inner` | keys in **both** | you need complete attributes on every row |
| `left` | all of the **left** | your spine must not shrink — **the analysis default** |
| `right` | all of the **right** | rarely; clearer as a `left` the other way round |
| `outer` | **everything** | reconciling two lists, when mismatches *are* the finding |

> **The moment to watch.** `inner` returns \$3,188,933. The raw total is \$3,250,242. It deleted the
> pop-up kiosk's entire \$61,310 and did not say a word. `indicator=True` and `validate=` are the two
> habits that catch it.

**2.2 — merging on two keys.** The roster is one row per outlet per week, so the key is the *pair*
`(outlet_id, week_start)`. `pd.Grouper` gets the sales to the same grain. Watch the dtypes: a text
`"2024-01-01"` never matches a `Timestamp("2024-01-01")`, and pandas reports zero matches rather
than an error.

**2.3 — `melt`: wide → long.** The target sheet has one column per month, so "month" is not a column
and cannot be a join key. `melt` folds the headers down into rows; then the merge works and a
variance column becomes possible. Note the kiosk's `NaN` target: honest, where `fillna(0)` would
have printed an infinite variance.

**2.4 — `pivot`: long → wide.** Long format is for computers; wide format is for people. Reshape at
the last minute, for reading. `pivot` fails on duplicate cells; `pivot_table` is the same operation
plus an aggregation, which is why duplicates are fine there.

---

## 🏃 Part 3: Aggregation & Reporting (45 min)

Continue with **Part 3**. Every table here follows the four beats — run through them before each one.

- **3.1 `groupby`** — split, apply, combine, on a six-row drill you can check by hand. Then two keys,
  a MultiIndex, and `.unstack()` — which *is* a pivot table.
- **3.2 `.agg()`** — named aggregation, several questions in one pass. `nunique` vs `count` vs `size`
  matters here: there are three rows per day, so `count` would claim 1,641 trading days.
- **3.3 `pivot_table`** — index, columns, values, aggfunc, plus `margins=True` for a free check. Then
  convert rows to percentages: OUT-01 and OUT-03 make half their money before 11am; OUT-04 makes a
  third in the evening. Same chain, two different businesses.
- **3.4 `crosstab`** — frequency, so it needs one row per event: switch to `tickets_week.csv`. Try
  `normalize="columns"`, then `values=` + `aggfunc=`.
- **3.5 correlation** — revenue vs staff hours, then `.corr()` across outlets. OUT-03 and OUT-04
  correlate at **-0.72** and neither causes the other; every number in the kiosk's row rests on
  **three** months of data. Use correlation to find candidates to investigate, never as the finding.

> **The payoff is the last cell:** revenue per staff hour for the last two quarters. Marina Bay earns
> **\$19.92** per staff hour against \$25–27 everywhere else. Revenue fell in November; the roster
> did not. That is a fixable problem worth real money, and it is entirely separate from the lease.

---

## 🏃 Part 4: From Table to Decision (20 min)

Continue with **Part 4**. Two cells: a like-for-like 2025 H1 vs 2024 H1 comparison per outlet, then
rent and staffing efficiency joined onto it.

| | Marina Bay | Raffles Place | Tampines Mall | Holland Village |
|---|---|---|---|---|
| 2025 H1 revenue | \$203,147 | \$309,339 | \$279,272 | \$253,450 |
| vs 2024 H1 | **−27.9%** | −1.5% | +1.3% | **+26.5%** |
| rent as % of revenue | **28.4%** | 15.9% | 14.6% | 14.7% |
| revenue per staff hour | **\$19.92** | \$26.36 | \$25.48 | \$26.72 |

> **Notice what the table does not say.** It does not say "close Marina Bay". It gives the owner the
> three numbers her decision needs, side by side. Recommending is her job; making the comparison
> possible was yours.

The cell saves `data/lesson19_decision.csv` and `data/lesson19_monthly_by_outlet.csv`. Lesson 1.10
opens both — a copy already ships in `1.10/data/` so nobody is blocked, but learners who run this
cell should compare their file with it.

---

## 🎯 Wrap-Up

**Key Takeaways:**
1. A date is a type. Nothing about time works until `pd.to_datetime` has run — and an unspecified
   day/month order fails silently, not loudly.
2. `resample` changes the grain of time; `rolling` smooths it. Use `rolling` to tell a step from a slope.
3. The `how` of a join is a business decision. `inner` silently deleted $61,310. Default to `left`,
   then check with `indicator=True`.
4. Long format is for computers, wide format is for people. `melt` before you join; `pivot` before you show.
5. Split-apply-combine is the engine: `groupby` → `.agg()` → `pivot_table` → `crosstab` are four
   faces of one idea.
6. Always run beat 4. Grouped totals must tie back to ungrouped totals.
7. Every aggregate hides as much as it reveals. The fix for a suspicious average is a finer grain.

**Next Steps:**
- Complete the [Assignment](./assignment.md) — the Q3 review pack.
- Next lesson: **1.10 Data Visualisation & Storytelling** — the owner gets 20 seconds and one slide.
  Your `decision` table has to survive the trip.
