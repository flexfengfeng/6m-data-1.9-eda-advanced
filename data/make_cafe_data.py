"""
Generate the "Daily Grind" café-chain dataset used as the spine for Lessons 1.9 and 1.10.

The numbers are synthetic. The *story* is deliberate:

  * Chain-level revenue looks FLAT across the last two quarters.
  * Underneath, Marina Bay (OUT-03) is falling and Holland Village (OUT-04) is rising.
    The flat total is two opposite trends cancelling out. That is the whole lesson.
  * A competitor opens beside Marina Bay on 2024-11-04 -> a step change, not a slope.
  * Weekday/weekend and daypart patterns differ by outlet (CBD dies at the weekend,
    residential outlets do not).
  * daily_sales.csv contains a pop-up kiosk (OUT-05) that is NOT in outlets.csv, and
    outlets.csv contains an outlet (OUT-06) that has not opened, so it has no sales.
    -> inner vs left vs outer join has a visible, explainable consequence.
  * targets_wide.csv is in the wide layout a manager would type into Excel, so it has
    to be melted before it can be merged with the actuals.

Files written next to this script:
  outlets.csv            5 rows      - the lookup table (merge key: outlet_id)
  daily_sales.csv        ~6.8k rows  - date x outlet x daypart: the time-series spine
  tickets_week.csv       ~4k rows    - one week of individual tickets (for distributions)
  roster.csv             ~330 rows   - weekly staff hours per outlet
  targets_wide.csv       4 x 19      - monthly targets, wide format (needs melting)
  monthly_by_outlet.csv  ~76 rows    - pre-aggregated monthly revenue, for Lesson 1.10

Run:  python make_cafe_data.py
"""

import os

import numpy as np
import pandas as pd

RNG = np.random.default_rng(20260729)
HERE = os.path.dirname(os.path.abspath(__file__))

START = pd.Timestamp("2024-01-01")
END = pd.Timestamp("2025-06-30")
TICKET_WEEK = (pd.Timestamp("2025-06-16"), pd.Timestamp("2025-06-22"))
COMPETITOR_OPENS = pd.Timestamp("2024-11-04")

# ---------------------------------------------------------------- outlets
OUTLETS = pd.DataFrame(
    [
        # id,      name,              region,    opened,       seats, monthly rent
        ("OUT-01", "Raffles Place", "Central", "2019-04-15", 28, 8200),
        ("OUT-02", "Tampines Mall", "East", "2020-09-01", 42, 6800),
        ("OUT-03", "Marina Bay", "Central", "2021-02-10", 24, 9600),
        ("OUT-04", "Holland Village", "Central", "2023-06-20", 36, 6200),
        ("OUT-06", "Sentosa Cove", "South", "2025-08-01", 30, 7500),  # not open yet
    ],
    columns=["outlet_id", "outlet_name", "region", "opened_date", "seats", "monthly_rent_sgd"],
)

# Average daily revenue per outlet at the start of the window.
BASE = {"OUT-01": 1850.0, "OUT-02": 1420.0, "OUT-03": 1680.0, "OUT-04": 980.0, "OUT-05": 620.0}

# Monthly compound drift. Marina Bay slides, Holland Village climbs.
DRIFT = {"OUT-01": 0.0015, "OUT-02": 0.0010, "OUT-03": -0.0260, "OUT-04": 0.0190, "OUT-05": 0.0}

# Weekday multipliers, Mon..Sun.
WEEKDAY = {
    "OUT-01": [1.12, 1.15, 1.14, 1.16, 1.10, 0.42, 0.30],
    "OUT-02": [0.86, 0.88, 0.92, 0.96, 1.10, 1.42, 1.34],
    "OUT-03": [1.10, 1.12, 1.12, 1.14, 1.08, 0.55, 0.40],
    "OUT-04": [0.94, 0.96, 0.98, 1.02, 1.18, 1.26, 1.18],
    "OUT-05": [1.00, 1.00, 1.02, 1.05, 1.15, 1.20, 1.10],
}

# Share of the day's takings by daypart.
DAYPART = {
    "OUT-01": {"Morning": 0.52, "Midday": 0.36, "Evening": 0.12},
    "OUT-02": {"Morning": 0.26, "Midday": 0.44, "Evening": 0.30},
    "OUT-03": {"Morning": 0.48, "Midday": 0.38, "Evening": 0.14},
    "OUT-04": {"Morning": 0.30, "Midday": 0.34, "Evening": 0.36},
    "OUT-05": {"Morning": 0.34, "Midday": 0.42, "Evening": 0.24},
}

# Menu: category -> (mean ticket value, spread, share of tickets)
MENU = [
    ("Coffee", 6.40, 0.95, 0.44),
    ("Tea", 5.40, 0.80, 0.11),
    ("Pastry", 5.20, 0.95, 0.19),
    ("Food", 14.50, 2.60, 0.22),
    ("Beans (retail)", 22.00, 3.50, 0.04),
]
CATS = [m[0] for m in MENU]
CAT_P = np.array([m[3] for m in MENU], dtype=float)
CAT_P /= CAT_P.sum()
PRICE = {m[0]: (m[1], m[2]) for m in MENU}
AVG_TICKET = sum(m[1] * m[3] for m in MENU)  # ~ $8.3

# What people buy depends on the time of day: coffee and a pastry on the way in,
# a proper meal at midday. This is what makes the ticket-value distribution
# genuinely two-humped in Lesson 1.10 instead of one smooth blob.
DAYPART_CAT = {
    #                Coffee  Tea  Pastry  Food  Beans
    "Morning": np.array([0.56, 0.10, 0.28, 0.04, 0.02]),
    "Midday": np.array([0.30, 0.10, 0.10, 0.46, 0.04]),
    "Evening": np.array([0.36, 0.14, 0.16, 0.28, 0.06]),
}
for _k, _v in DAYPART_CAT.items():
    DAYPART_CAT[_k] = _v / _v.sum()

# Average ticket implied by each daypart's basket. Morning is cheap (a coffee), midday
# is expensive (a meal). Using these instead of one global average is what keeps the
# per-daypart ticket counts - and therefore the prices - realistic.
_MEANS = np.array([m[1] for m in MENU])
AVG_TICKET_BY_PART = {k: float(_MEANS @ v) for k, v in DAYPART_CAT.items()}

PAYMENTS = ["PayNow", "Card", "Cash", "Wallet"]
PAY_P = [0.34, 0.40, 0.14, 0.12]
DAYPART_HOURS = {"Morning": (7, 11), "Midday": (11, 15), "Evening": (15, 21)}

HOLIDAYS = {
    "2024-01-01", "2024-02-10", "2024-02-11", "2024-03-29", "2024-04-10",
    "2024-05-01", "2024-05-22", "2024-08-09", "2024-10-31", "2024-12-25",
    "2025-01-01", "2025-01-29", "2025-01-30", "2025-03-31", "2025-04-18",
    "2025-05-01", "2025-05-12", "2025-06-07",
}


def month_index(day: pd.Timestamp) -> int:
    return (day.year - START.year) * 12 + (day.month - START.month)


def daily_target(outlet: str, day: pd.Timestamp) -> float:
    """Expected revenue for one outlet on one day, before random noise."""
    base = BASE[outlet] * (1 + DRIFT[outlet]) ** month_index(day)

    if outlet == "OUT-03":
        # Marina Bay is a STEP, not a slope - that distinction is the whole point of the
        # rolling-average section in Lesson 1.9. Nearly flat until the competitor opens on
        # 2024-11-04, then an abrupt drop to a new, slowly eroding level.
        m = month_index(day)
        base = BASE[outlet] * (1 - 0.004) ** m
        if day >= COMPETITOR_OPENS:
            base *= 0.80 * (1 - 0.010) ** max(m - month_index(COMPETITOR_OPENS), 0)

    if outlet == "OUT-04" and pd.Timestamp("2025-02-01") <= day <= pd.Timestamp("2025-03-31"):
        base *= 1.06  # loyalty campaign

    base *= WEEKDAY[outlet][day.dayofweek]
    if day.strftime("%Y-%m-%d") in HOLIDAYS:
        base *= 0.74
    base *= 1 + 0.025 * np.sin(2 * np.pi * (day.dayofyear - 60) / 365)
    return base


def outlet_days(outlet: str) -> pd.DatetimeIndex:
    if outlet == "OUT-05":  # pop-up kiosk, three months only
        return pd.date_range("2025-03-01", "2025-05-31", freq="D")
    return pd.date_range(START, END, freq="D")


ALL_OUTLETS = ["OUT-01", "OUT-02", "OUT-03", "OUT-04", "OUT-05"]


def build_daily_sales() -> pd.DataFrame:
    """One row per outlet, per day, per daypart."""
    rows = []
    for outlet in ALL_OUTLETS:
        for day in outlet_days(outlet):
            revenue = max(daily_target(outlet, day) * RNG.normal(1.0, 0.10), 80.0)
            for part, share in DAYPART[outlet].items():
                part_rev = revenue * share * RNG.normal(1.0, 0.07)
                tickets = max(
                    1, int(round(part_rev / AVG_TICKET_BY_PART[part] * RNG.normal(1.0, 0.05)))
                )
                items = int(round(tickets * RNG.normal(1.45, 0.06)))
                rows.append(
                    (
                        day.strftime("%Y-%m-%d"),
                        outlet,
                        part,
                        tickets,
                        items,
                        round(part_rev, 2),
                    )
                )
    return pd.DataFrame(
        rows, columns=["date", "outlet_id", "daypart", "tickets", "items", "revenue_sgd"]
    )


def build_tickets(daily: pd.DataFrame) -> pd.DataFrame:
    """Individual tickets for one week only - enough for distribution plots."""
    lo, hi = TICKET_WEEK
    week = daily[(daily["date"] >= lo.strftime("%Y-%m-%d")) & (daily["date"] <= hi.strftime("%Y-%m-%d"))]
    rows = []
    txn = 500000
    for _, r in week.iterrows():
        day = pd.Timestamp(r["date"])
        h0, h1 = DAYPART_HOURS[r["daypart"]]
        n = int(r["tickets"])
        # Build each ticket from the menu -- category first, then a price around that
        # category's mean. This is what keeps the distribution two-humped (a drink and a
        # pastry around $6; a meal around $14). Then scale the whole daypart by one factor
        # so the ticket totals still tie back to daily_sales.csv.
        cats = RNG.choice(CATS, size=n, p=DAYPART_CAT[r["daypart"]])
        base = np.array([max(RNG.normal(*PRICE[c]), 1.5) for c in cats])
        factor = r["revenue_sgd"] / base.sum()
        amounts = np.round(base * factor, 2)
        for cat, amt in zip(cats, amounts):
            cat = str(cat)
            amt = float(max(amt, 1.50))
            txn += 1
            stamp = day + pd.Timedelta(hours=h0, minutes=int(RNG.integers(0, (h1 - h0) * 60)))
            rows.append(
                (
                    f"T{txn}",
                    stamp.strftime("%Y-%m-%d %H:%M"),
                    r["outlet_id"],
                    r["daypart"],
                    cat,
                    # items has to be consistent with the amount, or learners who compute
                    # amount / items get nonsense like "$2.50 per coffee".
                    int(np.clip(round(amt / PRICE[cat][0]), 1, 5)),
                    amt,
                    str(RNG.choice(PAYMENTS, p=PAY_P)),
                )
            )
    out = pd.DataFrame(
        rows,
        columns=[
            "txn_id", "txn_datetime", "outlet_id", "daypart",
            "category", "items", "amount_sgd", "payment_method",
        ],
    )
    return out.sort_values("txn_datetime").reset_index(drop=True)


def build_roster(daily: pd.DataFrame) -> pd.DataFrame:
    """Weekly staffing per outlet. Follows LAST month's demand, so a declining outlet
    stays over-staffed - which is the point the owner needs to see."""
    d = daily.copy()
    d["date"] = pd.to_datetime(d["date"])
    weekly = (
        d.groupby(["outlet_id", pd.Grouper(key="date", freq="W-MON", label="left")])["revenue_sgd"]
        .sum()
        .reset_index()
        .rename(columns={"date": "week_start", "revenue_sgd": "week_revenue"})
    )
    rows = []
    for outlet, grp in weekly.groupby("outlet_id"):
        grp = grp.sort_values("week_start")
        # Drop the partial weeks at each end, or the roster shows an implausible 60 hours.
        full = grp["week_revenue"] > 0.55 * grp["week_revenue"].median()
        grp = grp[full]
        lagged = grp["week_revenue"].shift(4).bfill()
        if outlet == "OUT-03":
            # Marina Bay's roster was never re-cut after the competitor opened: staffing
            # freezes at the pre-November level. This is what makes it the least efficient
            # outlet in Part 3 - a fixable problem, separate from the lease decision.
            frozen = grp.loc[
                (grp["week_start"] >= "2024-09-01") & (grp["week_start"] < "2024-11-04"),
                "week_revenue",
            ].mean()
            lagged = lagged.where(grp["week_start"] < "2024-11-04", frozen)
        for (_, r), lag in zip(grp.iterrows(), lagged):
            hours = float(np.clip(lag / 26.0 * RNG.normal(1.0, 0.05), 80, 620))
            rows.append(
                (
                    outlet,
                    r["week_start"].strftime("%Y-%m-%d"),
                    round(hours, 1),
                    int(max(2, round(hours / 34))),
                )
            )
    return pd.DataFrame(rows, columns=["outlet_id", "week_start", "staff_hours", "headcount"])


def build_targets_wide(monthly: pd.DataFrame) -> pd.DataFrame:
    """Monthly revenue targets in the wide layout a manager types into Excel."""
    actual = monthly.pivot(index="outlet_id", columns="month", values="revenue_sgd")
    first_q = actual.iloc[:, :3].mean(axis=1)
    targets = {}
    for i, month in enumerate(actual.columns):
        targets[month] = (first_q * (1.04 ** (i / 12)) / 100).round() * 100
    wide = pd.DataFrame(targets)
    wide = wide.drop(index=[x for x in ["OUT-05"] if x in wide.index])
    return wide.reset_index()


def main() -> None:
    daily = build_daily_sales()
    tickets = build_tickets(daily)
    roster = build_roster(daily)

    d = daily.copy()
    d["month"] = pd.to_datetime(d["date"]).dt.to_period("M").astype(str)
    monthly = (
        d.groupby(["month", "outlet_id"])["revenue_sgd"].sum().round(2).reset_index()
    )
    targets = build_targets_wide(monthly)

    OUTLETS.to_csv(os.path.join(HERE, "outlets.csv"), index=False)
    daily.to_csv(os.path.join(HERE, "daily_sales.csv"), index=False)
    tickets.to_csv(os.path.join(HERE, "tickets_week.csv"), index=False)
    roster.to_csv(os.path.join(HERE, "roster.csv"), index=False)
    targets.to_csv(os.path.join(HERE, "targets_wide.csv"), index=False)
    monthly.to_csv(os.path.join(HERE, "monthly_by_outlet.csv"), index=False)

    print(f"daily_sales   : {len(daily):>6} rows   {daily['date'].min()} -> {daily['date'].max()}")
    print(f"tickets_week  : {len(tickets):>6} rows   {tickets['txn_datetime'].min()} -> {tickets['txn_datetime'].max()}")
    print(f"roster        : {len(roster):>6} rows")
    print(f"targets_wide  : {targets.shape[0]} rows x {targets.shape[1]} cols")
    print(f"monthly       : {len(monthly):>6} rows")
    print(f"avg ticket    : ${AVG_TICKET:.2f}")
    print()
    q = daily.copy()
    q["quarter"] = pd.to_datetime(q["date"]).dt.to_period("Q").astype(str)
    print("Chain revenue by quarter (the 'flat' headline):")
    print(q.groupby("quarter")["revenue_sgd"].sum().round(0).to_string())
    print()
    print("Same period, split by outlet (the real story):")
    print(
        q.pivot_table(index="quarter", columns="outlet_id", values="revenue_sgd", aggfunc="sum")
        .round(0)
        .to_string()
    )
    print()
    print("Excluding the pop-up kiosk (OUT-05), chain revenue by quarter:")
    print(
        q[q["outlet_id"] != "OUT-05"].groupby("quarter")["revenue_sgd"].sum().round(0).to_string()
    )


if __name__ == "__main__":
    main()
