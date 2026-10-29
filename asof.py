"""Lab 16: keep only index values knowable on a chosen decision date."""

import csv
import sys
from collections import namedtuple
from datetime import date, timedelta
from pathlib import Path


# Editable inputs. Each row number identifies the corresponding course training row.
DECISION_DATE = "2026-03-31"
DECISION_DATES = ["2026-02-28", "2026-03-31", "2026-04-30"]
RUN_AS_OF = "2026-10-28"  # Last completed month-end is September 2026.
Row = namedtuple("Row", "number ticker month published index")
ROWS = [
    Row(1, "AAA", "2026-01", "2026-02-10", 101.0),
    Row(2, "AAA", "2026-02", "2026-03-10", 104.0),
    Row(3, "AAA", "2026-03", "2026-04-10", 109.0),
    Row(4, "AAA", "2026-02", "2026-03-25", 103.0),
    Row(5, "BBB", "2026-01", "2026-02-10", 98.0),
    Row(6, "BBB", "2026-02", "2026-03-10", 97.0),
    Row(7, "BBB", "2026-02", "2026-03-10", 97.0),
    Row(8, "BBB", "2026-03", "2026-04-10", 92.0),
    Row(9, "CCC", "2026-01", "2026-02-10", 110.0),
    Row(10, "CCC", "2026-02", "2026-04-05", 112.0),
    Row(11, "", "2026-02", "2026-03-10", 99.0),
    Row(12, "CCC", "2026-02", "2026-03-10", 111.0),
]


def latest_publications(rows):
    """Keep the newest published value for each ticker and measured month."""
    chosen = {}
    replaced = []
    for row in rows:
        key = (row.ticker, row.month)
        prior = chosen.get(key)
        if prior is None:
            chosen[key] = row
        elif row.published > prior.published:
            replaced.append(prior)
            chosen[key] = row
        elif row.published < prior.published:
            replaced.append(row)
        else:
            raise ValueError(f"Conflicting publications on the same date: rows {prior.number}, {row.number}")
    return sorted(chosen.values(), key=lambda row: (row.ticker, row.month)), replaced


def signal(rows, ticker):
    """Return (percent change, latest month, latest row) for consecutive months."""
    by_month = {row.month: row for row in rows if row.ticker == ticker}
    if not by_month:
        return None
    latest_month = max(by_month)
    previous_month = (date.fromisoformat(latest_month + "-01") - timedelta(days=1)).strftime("%Y-%m")
    if previous_month not in by_month:
        return None
    latest = by_month[latest_month]
    previous = by_month[previous_month]
    return (latest.index / previous.index - 1) * 100, latest_month, latest


def show_removal(label, rows):
    numbers = ", ".join(str(row.number) for row in sorted(rows, key=lambda row: row.number)) or "none"
    print(f"{label}: {len(rows)} removed; rows {numbers}")


def main(decision_date=DECISION_DATE):
    cutoff = date.fromisoformat(decision_date)
    if len({row.number for row in ROWS}) != len(ROWS):
        raise ValueError("Row numbers must be unique")
    for row in ROWS:
        date.fromisoformat(row.month + "-01")
        date.fromisoformat(row.published)
        if row.index <= 0:
            raise ValueError(f"Index must be positive in row {row.number}")

    # Rule 1: unknown ticker cannot be assigned to a series.
    quarantined = [row for row in ROWS if not row.ticker.strip()]
    identified = [row for row in ROWS if row.ticker.strip()]

    # Rule 2: row number is an identifier, not part of the economic observation.
    seen = set()
    unique = []
    duplicates = []
    for row in identified:
        observation = (row.ticker, row.month, row.published, row.index)
        if observation in seen:
            duplicates.append(row)
        else:
            seen.add(observation)
            unique.append(row)

    # Rule 3: a later publication was unavailable at the decision date.
    late = [row for row in unique if date.fromisoformat(row.published) > cutoff]
    knowable = [row for row in unique if date.fromisoformat(row.published) <= cutoff]

    # Rule 4: among knowable publications for a ticker/month, take the newest.
    asof_panel, replaced = latest_publications(knowable)

    print(f"Decision date: {decision_date}")
    print("Row funnel")
    show_removal("1. Quarantined: no ticker", quarantined)
    show_removal("2. Exact duplicates", duplicates)
    show_removal("3. Published after decision date", late)
    show_removal("4. Older vintages replaced", replaced)
    print("As-of panel")
    print("Row  Ticker  Month     Published   Index")
    for row in asof_panel:
        print(f"{row.number:>3}  {row.ticker:<6}  {row.month}  {row.published}  {row.index:>5.1f}")

    # Naive panel uses the same valid, deduplicated observations, but no cutoff.
    naive_panel, _ = latest_publications(unique)
    print("Signals (latest measured month versus its previous month)")
    for ticker in sorted({row.ticker for row in unique}):
        asof_result = signal(asof_panel, ticker)
        naive_result = signal(naive_panel, ticker)
        for label, result in (("As-of", asof_result), ("Naive", naive_result)):
            if result is None:
                print(f"{ticker} {label}: unavailable (consecutive months needed)")
                continue
            change, month, latest = result
            month_name = date.fromisoformat(month + "-01").strftime("%B")
            # Identify a post-decision revision of the naive latest month.
            revised_later = (
                label == "Naive"
                and date.fromisoformat(latest.published) > cutoff
                and any(
                    row.ticker == ticker and row.month == month and row.published < latest.published
                    for row in unique
                )
            )
            suffix = ", revised" if revised_later else ""
            print(f"{ticker} {label}: {change:+.2f}% ({month_name}{suffix})")


def month_end(month):
    """Return the final calendar day of a YYYY-MM observation month."""
    first = date.fromisoformat(month + "-01")
    next_month = (first.replace(day=28) + timedelta(days=4)).replace(day=1)
    return next_month - timedelta(days=1)


def filter_on(rows, decision_date):
    """Apply the Lab 16 rules in order and return both panels and the funnel."""
    cutoff = date.fromisoformat(decision_date)
    if len({row.number for row in rows}) != len(rows):
        raise ValueError("Row numbers must be unique")
    for row in rows:
        month_end(row.month)
        date.fromisoformat(row.published)
        if row.index <= 0:
            raise ValueError(f"Index must be positive in row {row.number}")

    quarantined = [row for row in rows if not row.ticker.strip()]
    identified = [row for row in rows if row.ticker.strip()]
    seen = set()
    unique = []
    duplicates = []
    for row in identified:
        observation = (row.ticker, row.month, row.published, row.index)
        if observation in seen:
            duplicates.append(row)
        else:
            seen.add(observation)
            unique.append(row)
    late = [row for row in unique if date.fromisoformat(row.published) > cutoff]
    knowable = [row for row in unique if date.fromisoformat(row.published) <= cutoff]
    asof_panel, replaced = latest_publications(knowable)
    naive_panel, _ = latest_publications(unique)
    funnel = (quarantined, duplicates, late, replaced)
    leaks = sorted(
        row.number for row in naive_panel
        if month_end(row.month) <= cutoff and date.fromisoformat(row.published) > cutoff
    )
    return asof_panel, naive_panel, funnel, leaks


def report_dates(rows, decision_dates, label):
    """Print as-of signals and naive future-publication leaks for each date."""
    print(f"\n{label}")
    print("Date        As-of signal by series                         Naive unpublished rows  Funnel Q/D/L/R")
    for decision_date in decision_dates:
        asof_panel, _, funnel, leaks = filter_on(rows, decision_date)
        signals = []
        for ticker in sorted({row.ticker for row in rows if row.ticker.strip()}):
            result = signal(asof_panel, ticker)
            signals.append(f"{ticker} {result[0]:+.2f}%" if result else f"{ticker} not enough knowable months")
        leak_text = ", ".join(map(str, leaks)) or "none"
        funnel_text = "/".join(str(len(part)) for part in funnel)
        print(f"{decision_date}  {'; '.join(signals):<50} {leak_text:<24} {funnel_text}")


def read_csv(path):
    """Read a named series table with the Lab 16 observation fields."""
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"row", "series name", "month measured", "published on", "value"}
        if not reader.fieldnames or set(reader.fieldnames) != required:
            raise ValueError(f"CSV columns must be: {', '.join(sorted(required))}")
        rows = [
            Row(int(item["row"]), item["series name"], item["month measured"],
                item["published on"], float(item["value"]))
            for item in reader
        ]
    if not rows:
        raise ValueError("CSV has no observations")
    return rows


def last_completed_month_ends(as_of, count=24):
    """Return the last count completed month-ends, oldest first."""
    current = date.fromisoformat(as_of).replace(day=1) - timedelta(days=1)
    dates = []
    for _ in range(count):
        dates.append(current.isoformat())
        current = current.replace(day=1) - timedelta(days=1)
    return dates[::-1]


if __name__ == "__main__":
    main()
    report_dates(ROWS, DECISION_DATES, "Lab 17 training dates (Q/D/L/R = quarantined/duplicate/late/replaced)")
    if len(sys.argv) > 2:
        raise SystemExit("Usage: python asof.py [series_table.csv]")
    if len(sys.argv) == 2:
        report_dates(read_csv(sys.argv[1]), last_completed_month_ends(RUN_AS_OF),
                     f"CSV series: {sys.argv[1]} (as of {RUN_AS_OF})")
