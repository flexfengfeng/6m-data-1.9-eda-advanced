# 📚 Pre-Class: Advanced EDA — Time, Joins, Shape and Groups

⏱️ **Estimated Time:** 35–40 minutes
**Prerequisites:** Lesson 1.8 — EDA Basic

> In Lesson 1.8 you cleaned one month of The Daily Grind's raw till export: money stored as text,
> twelve spellings for four cafés, sentinel codes, a mis-keyed \$98,000, a duplicated batch. You ended
> with rows you could trust. This lesson asks the next question — **so what?** Trustworthy rows still
> do not tell you anything until you group them, and to group them well you need four ideas: time as a
> type, joins, shape, and split-apply-combine.
>
> You are now working on the same export for **all 18 months**, already cleaned the way you cleaned
> June: `data/daily_sales.csv`.

🎯 **Goal:** build the mental model *before* you meet the syntax. Understanding the *why* makes the
code almost boring, which is the aim.

🎬 Watch this video: [[Advanced EDA: The Analytical Autopsy]](https://youtu.be/g4SoOl3G7Hs)

---

## **0. The problem you will be working on (3 minutes)**

> **The Daily Grind** is a four-outlet café chain in Singapore. Revenue has been **flat for two
> quarters**. The Marina Bay lease is up for renewal this month — $9,600 a month — and the owner
> has to sign or walk away. She hands you 18 months of daily sales and asks: *what is going on?*

Hold this question in mind as you read. Every tool below exists because a flat total is not an
answer, and the whole lesson is one long attempt to get behind it.

Here is the punchline, so you can watch it arrive: the chain total is flat because **one outlet is
falling and another is rising by almost the same amount**. Nothing in Lesson 1.8 could have found
that. It is invisible at the level of a total and obvious the moment you group by outlet.

---

## **1. Time is a type, not a string (8 minutes)**

**The problem.** To a computer, `"2023-01-01"` is text, exactly like `"Hello World"`. It has no idea
that `"2023-01-02"` comes a day later. Sorted as text, `"2024-10-02"` comes *before* `"2024-9-30"`,
because the character `1` sorts before `9`.

**The fix.** Convert text into **datetime objects** (`pd.to_datetime`). Then dates behave like time:
you can subtract them, sort them, and ask which day of the week they were.

**The trap that catches everyone.** Is `03/06/2025` the 3rd of June or the 6th of March? Singapore
and the UK write day first; the US writes month first. Pandas has to guess unless you tell it — and
here is the cruel part: **days 1–12 parse "successfully" either way, so no error appears.** Your
report is silently wrong by up to three months and looks perfectly healthy.

Three ideas built on top of datetimes, which you will use in class:

| Idea | In one line | Café example |
|---|---|---|
| **Resample** | Change the grain of time | 547 daily rows → 18 monthly rows |
| **Rolling** | Average over a moving window | A 7-day average cancels the weekend dip |
| **Step vs slope** | *When* did it change? | A step means something happened on a date; a slope means a slow drift |

That last row is the important one. "Revenue is down 21%" is not actionable. "Revenue dropped 21% in
the first week of November and has been flat at the new level since" tells you where to look —
and a rolling average is how you see the difference.

📖 Reading: [Python Datetime Tutorial](https://www.programiz.com/python-programming/datetime)

---

## **2. Joins: giving a row its meaning (8 minutes)**

The sales file says `OUT-03`. It does not say "Marina Bay", and it knows nothing about rent, seats or
staffing. Those live in other files. A **join** (in pandas, `merge`) lines up two tables on a shared
**key** column — here, `outlet_id`.

**The party analogy.** You have a guest list and an RSVP list.

| Join | Who gets in | Real consequence |
|---|---|---|
| **Inner** | only people on **both** lists | anyone missing from either list disappears — silently |
| **Left** | everyone on the **guest list**, RSVP where known | your main list never shrinks |
| **Right** | everyone on the **RSVP list** | the mirror image of left |
| **Outer** | **everyone** on either list | the mismatches are visible, which is sometimes the point |

**Why this is not trivia.** In class you will run all four on the café data. The inner join returns a
revenue total **$61,310 short** — a pop-up kiosk exists in the sales file but was never added to the
outlet list, so the inner join drops it. It does not warn you. It returns a smaller number that looks
completely reasonable.

**Rule of thumb:** default to `left` (keep your spine), then check for the blanks it leaves.

---

## **3. Tidy data: wide vs long (7 minutes)**

The same numbers can sit in two layouts, and it matters which one you are in.

**Wide (spreadsheet style)** — great for humans reading it:

| outlet | 2024-01 | 2024-02 | 2024-03 |
|---|---|---|---|
| OUT-01 | 53,744 | 49,725 | 51,932 |

**Long (database style)** — great for code:

| outlet | month | revenue |
|---|---|---|
| OUT-01 | 2024-01 | 53,744 |
| OUT-01 | 2024-02 | 49,725 |
| OUT-01 | 2024-03 | 51,932 |

**Why long wins for analysis.** In the wide layout, "month" is not a column — it is a set of column
*headers*. You cannot group by it, filter it, or join on it, because it does not exist as data.
Fold the headers down into a column and all three become possible.

- **`melt`** = wide → long (fold headers down into rows)
- **`pivot`** = long → wide (spread a column across the top)

**The habit:** melt to compute, pivot to present. Reshape into wide format at the last possible
moment, for human eyes only.

---

## **4. Split-Apply-Combine (7 minutes)**

This is the logic behind `groupby`, and behind Excel pivot tables. Three steps, always in this order:

1. **Split** the rows into groups (e.g. split café sales by outlet).
2. **Apply** a calculation to each group independently (e.g. add up revenue).
3. **Combine** the answers into one summary table.

Before you write any of it, answer four questions. These are the **four beats** used all through the
lesson, and they are worth more than any single method:

| Beat | Ask yourself | Café example |
|---|---|---|
| **1. Question** | What decision does this number serve? | Renew the Marina Bay lease — yes or no? |
| **2. Grain** | One row per **what**? | One row per outlet, per month |
| **3. Aggregation** | Sum, mean or count — and **why that one**? | Sum for totals, mean for efficiency |
| **4. Check** | Does the total still tie back? | Grouped total must equal the ungrouped total |

Beat 3 has teeth. February's *total* revenue drops every year — because February is short, not
because business is bad. The *average trading day* barely moves. Same data, two aggregations, two
completely different stories, and only one of them is real.

Beat 4 is the one everybody skips, and it is the one that catches the $61,310.

---

## **5. Correlation vs covariance (2 minutes)**

* **The question:** do two things move together? (Say, revenue and staff hours.)
* **Covariance** answers it, but the number's size depends on the units, so on its own it is
  unreadable. Is 111,930 a strong relationship? Unanswerable.
* **Correlation** is covariance rescaled to sit between **−1 and 1**: `1` = move identically,
  `−1` = move exactly opposite, `0` = no linear relationship. Readable, comparable.
* **The warning you must carry into class:** two of the cafés are correlated at **−0.72** and neither
  affects the other at all. One is declining, one is growing, over the same 18 months. Correlation
  cannot tell a shared timeline from a cause. Use it to *find candidates to investigate*, never as
  the finding itself.

📖 Reading: [What's the Difference Between Covariance and Correlation](https://careerfoundry.com/en/blog/data-analytics/covariance-vs-correlation/)

---

## **6. Preparation checklist (2 minutes)**

1. **Environment:** the `pds` conda environment from Lesson 1.7. If it is not set up:
   `conda env create -f environment.yml`, then `conda activate pds`.
2. **Check it works:** in a notebook cell, run `import pandas as pd; import numpy as np` — no errors
   means you are ready.
3. **Data:** already in `data/`. Nothing to download. If you want to see how it was made, read
   `data/make_cafe_data.py`.
4. **Mindset:** you are not learning five methods today. You are learning to ask *one row per what?*
   before you type anything.

---

## **🤖 AI Companion Exercise (recommended)**

Paste these into Claude or ChatGPT. Good substitute for a study group if you are learning solo.

**Prompt 1 (joins):** "Explain the difference between an inner join and a left join using the
analogy of inviting friends to two different parties. What happens to the friends who are only on
one list? Then give me a business example where an inner join would produce a wrong number without
raising any error."

**Prompt 2 (reshaping):** "Explain the difference between pandas `pivot` and `melt` using a
spreadsheet of student grades. Show the same data in both layouts and explain which one you would
use to make a chart, and why."

**Prompt 3 (grouping):** "Explain split-apply-combine using a grocery cart of different fruit types.
Then explain why the average of a group can hide the thing you actually needed to see."

---

## **🧠 Quick Self-Check**

Answer these without scrolling up, then check below.

1. **Scenario:** a column of dates reads `01/06/2025`, `02/06/2025`, `13/06/2025`. You load it
   without telling pandas the format and no error appears. Should you relax?
2. **True or false:** an inner join can make your revenue total smaller without producing any error
   or warning.
3. **Scenario:** you have monthly revenue in a spreadsheet with one column per month, and a separate
   table of monthly targets in long format. What do you have to do before you can compare them?
4. **Scenario:** chain revenue has been flat for two quarters. Your manager concludes "nothing is
   changing". What is the one question you would ask?
5. **Definition:** in one sentence each — what does `resample` do, and what does `rolling` do?

<details>
<summary>💡 Suggested answers</summary>

**Q1:** No — the opposite. The absence of an error is the danger. Pandas guessed a format from the
first values, and since days 1–12 are valid as both days and months, a wrong guess parses without
complaint. `13/06/2025` is the only value that *forces* day-first, and if it had not been there you
would never know. Always pass `format=` or `dayfirst=True`.

**Q2:** True, and this is the single most useful thing in this pre-class. An inner join keeps only
keys present in *both* tables. Rows whose key is missing from the lookup table are dropped, along
with their revenue. Pandas considers that a correct answer to the question you asked. Default to a
left join and inspect the blanks.

**Q3:** Reshape one of them so they share a layout — in practice, `melt` the wide sheet so that
"month" becomes a real column. Only then is there a key to join on. You could pivot the long table
instead, but melting is nearly always the better move: compute in long format, present in wide.

**Q4:** "Flat *at what grain*?" A flat total is often two opposite movements cancelling out. Split by
outlet, region, product or customer segment and see whether the flatness survives. In this lesson it
does not: one café is down 28% and another is up 27%.

**Q5:** `resample` changes the grain of time — it buckets rows into days, weeks or months and
aggregates each bucket (it is `groupby` for dates). `rolling` keeps the original rows but replaces
each value with a statistic over a moving window of neighbouring rows, which smooths out noise so
the trend is visible.

</details>

---

## **Reference**

- [Pandas Data Wrangling Cheatsheet](https://www.datacamp.com/cheat-sheet/pandas-cheat-sheet-data-wrangling-in-python)
- [Working with Dates and Times in Python](https://www.datacamp.com/cheat-sheet/working-with-dates-and-times-in-python-cheat-sheet)
- [Tidy Data (Hadley Wickham's original paper — the source of "long format")](https://vita.had.co.nz/papers/tidy-data.pdf)

If anything above is unclear, post in **#questions** on Discord before class — that is exactly what
the channel is for.
