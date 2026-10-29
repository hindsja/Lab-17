# Lab 17 — Point-in-Time Audit

## Training table

`python asof.py` preserves the Lab 16 printout and adds the three decision-date report. All three dates match the [Lab 17 known answer](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-10/lab-17-point-in-time.md):

| Decision date | As-of signal | Naive rows for completed months, published later |
|---|---|---|
| 2026-02-28 | Not enough knowable months for AAA, BBB, or CCC | 4, 6, 10 |
| 2026-03-31 | AAA +1.98%; BBB −1.02%; CCC +0.91% | 3, 8, 10 |
| 2026-04-30 | AAA +5.83%; BBB −5.15%; CCC +1.82%, equal to naive | None |

The 31 March funnel remains: quarantine row 11; remove duplicate row 7; exclude late rows 3, 8, 10; replace older vintage row 2. The as-of panel is rows 1, 4, 5, 6, 9, 12.

## Data card: U.S. unemployment rate (UNRATE)

| Field | Evidence and interpretation |
|---|---|
| Source | [ALFRED UNRATE series](https://alfred.stlouisfed.org/series?seid=UNRATE), sourced from the U.S. Bureau of Labor Statistics (BLS); [ALFRED vintage-date download page](https://alfred.stlouisfed.org/series/downloaddata?seid=UNRATE). |
| Measure | Unemployed people as a share of the U.S. civilian labor force, from the Current Population Survey (household survey). This is a possible macroeconomic context series for a four-fund universe of EWY, QQQM, VOO, and FNDX; it is not a demonstrated predictor of their returns. |
| Units and frequency | Percent of labor force; monthly; seasonally adjusted. A move from 4.1% to 4.2% is **0.1 percentage point**. The lab's `(new / old − 1) × 100` signal calls that a **2.44% relative change**, not a 2.44-percentage-point rise. |
| Publication lag | Among the 26 first releases in the table, 1–51 calendar days after the measured month ended (median 6 days). September 2025 was released on 2025-11-20, 51 days after month-end, following the lapse in appropriations. [BLS revised release dates](https://www.bls.gov/bls/2025-lapse-revised-release-dates.htm) confirm that delay. |
| Revisions and gaps | Five measured months have a later changed value: July 2024; February, May, July, and November 2025. October 2025 has no UNRATE observation: BLS says the household survey was not collected for that reference month. [BLS explanation](https://www.bls.gov/bls/2025-lapse-revised-release-dates.htm). |
| Download date | 2026-10-28. The CSV contains 31 first-release or changed-value rows for 26 observed months, July 2024–September 2026, across a 27-calendar-month span because October 2025 is missing. |

The `published on` column is the ALFRED vintage date when a value first appeared or changed. ALFRED says its release dates use the source's actual release date when available; otherwise it uses a provider date or the first date the series was available in FRED. [ALFRED help](https://alfred.stlouisfed.org/help). The [ALFRED output-format guide](https://alfred.stlouisfed.org/help/downloaddata) distinguishes an observation's measured date from its vintage date. Unchanged carry-forward values are omitted from the CSV because they are not new publications of that observation.

Three source-file spot checks performed in this workspace, using separately downloaded ALFRED vintage CSVs:

| CSV row | ALFRED vintage source | Measured month | Value in vintage |
|---:|---|---|---:|
| 1 | [2024-08-02](https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=UNRATE&vintage_date=2024-08-02) | 2024-07 | 4.3% |
| 16 | [2025-11-20](https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=UNRATE&vintage_date=2025-11-20) | 2025-09 | 4.4% |
| 21 | [2026-01-09](https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=UNRATE&vintage_date=2026-01-09) | 2025-11 | 4.5% (revised from 4.6%) |

The series name, measured month, vintage publication date, and value make the data card useful for a backtest: they show which value was eligible on each decision date. “Cleaned the data” describes a processing step but supplies none of that timing, unit, or revision evidence.

## Own-series run

Command: `python asof.py lab17_unrate_vintages.csv`. The 24 completed month-ends are October 2024 through September 2026, based on the 2026-10-28 run date. The CSV has 0 unidentified series and 0 exact duplicates. At the final decision date, 2026-09-30, the funnel excludes one late row (31, the September value published October 2) and replaces five older vintages (rows 1, 9, 12, 14, 17).

| Decision date | As-of relative change | Naive rows not yet published for completed months |
|---|---:|---|
| 2024-10-31 | −2.38% | 2: 4, 6 |
| 2024-11-30 | +0.00% | 2: 5, 6 |
| 2024-12-31 | +2.44% | 2: 6, 7 |
| 2025-01-31 | −2.38% | 1: 8 |
| 2025-02-28 | −2.44% | 1: 18 |
| 2025-03-31 | +2.50% | 2: 10, 18 |
| 2025-04-30 | +2.44% | 2: 11, 18 |
| 2025-05-31 | +0.00% | 2: 18, 19 |
| 2025-06-30 | +0.00% | 3: 13, 18, 19 |
| 2025-07-31 | −2.38% | 3: 18, 19, 20 |
| 2025-08-31 | +2.44% | 4: 15, 18, 19, 20 |
| 2025-09-30 | +2.38% | 4: 16, 18, 19, 20 |
| 2025-10-31 | +2.38% | 4: 16, 18, 19, 20 |
| 2025-11-30 | +2.33% | 4: 18, 19, 20, 21 |
| 2025-12-31 | Not enough knowable consecutive months | 5: 18, 19, 20, 21, 22 |
| 2026-01-31 | −2.22% | 1: 23 |
| 2026-02-28 | −2.27% | 1: 24 |
| 2026-03-31 | +2.33% | 1: 25 |
| 2026-04-30 | −2.27% | 1: 26 |
| 2026-05-31 | +0.00% | 1: 27 |
| 2026-06-30 | +0.00% | 1: 28 |
| 2026-07-31 | −2.33% | 1: 29 |
| 2026-08-31 | −2.38% | 1: 30 |
| 2026-09-30 | +0.00% | 1: 31 |

For example, the September 2025 value of 4.4% was unavailable at the September 30 or October 31 decision dates; it was published November 20. At December 31, the newest knowable observation was November 2025, but October 2025 was never collected, so the required consecutive-month signal is unavailable. No value was filled across that gap.

## Project 2 call

**Quarantine UNRATE for Project 2 until the portfolio backtest consumes these vintage rows through the as-of filter and abstains whenever two consecutive knowable months are unavailable.** At a month-end decision after the day's releases, admit only rows whose publication date is on or before that decision date, then keep the latest eligible vintage per measured month. Reconsider the quarantine after the integrated backtest proves those rules, defines how the missing October 2025 month is handled, and tests whether this macro series adds value against a price-only baseline outside the period used to choose the rule.

A naive backtest using today's UNRATE history would give earlier decisions the delayed September 2025 reading and later revisions to five months. That would overstate what the strategy knew at the time; this lab does **not** measure how much portfolio return or predictive accuracy would change.

## Verification and attribution

The Python commands `python asof.py` and `python asof.py lab17_unrate_vintages.csv` exited successfully on 2026-10-28. The training signals and leak rows matched the course's three dates; the CSV report printed all 24 completed month-ends. ALFRED vintage snapshots were downloaded and compared by script, with the three spot checks above read separately from their raw CSVs. The table construction, code extension, run, and written analysis were AI-assisted. The source data are from ALFRED/BLS; the training answer is course-provided. These checks do not represent a student-performed hand read or a partner exchange.
