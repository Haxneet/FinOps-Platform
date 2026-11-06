# Intelligent Cloud FinOps Platform

Term project: a Streamlit dashboard for cloud cost visibility, planning and optimization, using Floci to emulate AWS services locally and Python/Boto3 to retrieve data.

## Team and module ownership

| Module | Page | Owner |
|---|---|---|
| 1 Pricing Explorer | pages/2_Pricing_Explorer.py | Areeba (TBC) |
| 2 Cost Explorer | pages/3_Cost_Explorer.py | Areeba (TBC) |
| 3 Infrastructure Builder | pages/4_Infrastructure_Builder.py | Bhawan |
| 4 Cost Estimator | pages/5_Cost_Estimator.py | Bhawan |
| 5 Pricing Comparison | pages/6_Pricing_Comparison.py | Areeba (TBC) |
| 6 Workload Simulator | pages/7_Workload_Simulator.py | Harneet |
| 7 Cost Optimizer | pages/8_Cost_Optimizer.py | Areeba (TBC) |
| 8 Reporting | pages/14_Reports.py | Areeba (TBC) |
| 9 Budget Management | pages/9_Budget_Management.py | Bhawan |
| 10 Resource Utilization | pages/10_Resource_Utilization.py | Areeba (TBC) |
| 11 Cost Allocation | pages/11_Cost_Allocation.py | Areeba (TBC) |
| 12 Scaling Analysis | pages/12_Scaling_Analysis.py | Harneet |
| 13 Storage and Backup | pages/13_Storage_and_Backup.py | Harneet |
| Home page | app.py | Areeba (TBC) |

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then edit values
streamlit run app.py
```

Floci setup notes are in `docs/floci_setup.md`.

## Project layout

```
app.py                 Home page (entry point)
pages/                 One file per dashboard page (Streamlit multipage)
common/                Shared code: Floci client, data loading, labels, cost math
data/sample/           Sample and synthetic datasets (CSV)
docs/                  Setup, assumptions, documentation
reports/               Generated cost reports
screenshots/           Dashboard screenshots for submission
```

## Rules the whole team follows

1. Simulated data must be labelled. Use `data_source_notice("simulated")` or `("actual")` from `common/banners.py` on every page.
2. Every cost calculation documents: pricing source, region, configuration, usage, billing period, pricing model, assumptions.
3. Shared datasets live in `data/sample/` and are documented in `data/sample/README.md`. Do not change a column name without telling the others.
4. Use `common/floci.py` to create AWS clients. Do not hardcode endpoints.

See `CONTRIBUTING.md` for the git workflow.
