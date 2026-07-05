"""
Report step.

Builds a single self-contained HTML report: charts are embedded as base64 so
the file can be opened or shared without the reports/figures/ folder.
"""

from __future__ import annotations

import base64
import datetime as dt
from pathlib import Path

import pandas as pd


def _img_tag(png_path: Path) -> str:
    """Embed a PNG as a base64 <img> so the report is fully self-contained."""
    data = base64.b64encode(png_path.read_bytes()).decode("ascii")
    return f'<img src="data:image/png;base64,{data}" alt="{png_path.stem}">'


def _kpi_cards(kpis: dict) -> str:
    cards = [
        ("Total movies", f"{kpis['total_movies']:,}"),
        ("Years covered", f"{kpis['year_min']}–{kpis['year_max']}"),
        ("Average rating", f"{kpis['avg_rating']}"),
        ("With financials", f"{kpis['movies_with_financials']:,}"),
        ("Total revenue", f"${kpis['total_revenue_b']}B"),
        ("Median runtime", f"{kpis['median_runtime']:.0f} min"),
    ]
    return "".join(
        f'<div class="card"><div class="v">{v}</div><div class="k">{k}</div></div>'
        for k, v in cards
    )


def _validation_html(reports: list) -> str:
    rows = []
    for rep in reports:
        for c in rep.checks:
            badge = "ok" if c.passed else "bad"
            label = "PASS" if c.passed else "FAIL"
            rows.append(
                f"<tr><td>{rep.gate}</td><td>{c.name}</td>"
                f'<td><span class="badge {badge}">{label}</span></td>'
                f"<td>{c.detail}</td></tr>"
            )
    return "".join(rows)


def build_report(kpis: dict, cleaning_summary: dict, validation_reports: list,
                 figures: list[Path], tables: dict[str, pd.DataFrame], cfg: dict,
                 logger=None) -> Path:
    """Assemble the HTML report and return its path."""
    out = Path(cfg["paths"]["report_html"])
    out.parent.mkdir(parents=True, exist_ok=True)

    charts_html = "\n".join(
        f'<figure>{_img_tag(p)}<figcaption>{p.stem.replace("_", " ").title()}'
        f"</figcaption></figure>"
        for p in figures
    )

    def table_block(title: str, key: str) -> str:
        if key not in tables:
            return ""
        html_table = tables[key].to_html(index=False, border=0, justify="left")
        return f"<h3>{title}</h3>{html_table}"

    tables_html = "\n".join([
        table_block("Top Rated Movies", "top_rated"),
        table_block("Top Grossing Movies", "top_revenue"),
        table_block("Best ROI Movies", "top_roi"),
        table_block("Genre Breakdown", "genre_stats"),
    ])

    clean_rows = "".join(
        f"<tr><td>{k.replace('_', ' ').title()}</td><td>{v:,}</td></tr>"
        if isinstance(v, int) else f"<tr><td>{k.replace('_', ' ').title()}</td><td>{v}</td></tr>"
        for k, v in cleaning_summary.items()
    )

    generated = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    html = _TEMPLATE.format(
        project=cfg["project"]["name"],
        generated=generated,
        kpi_cards=_kpi_cards(kpis),
        clean_rows=clean_rows,
        validation_rows=_validation_html(validation_reports),
        charts=charts_html,
        tables=tables_html,
    )
    out.write_text(html, encoding="utf-8")
    if logger:
        logger.info("Report written to %s", out)
    return out


_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{project} — Report</title>
<style>
  :root {{ --bg:#0f1117; --panel:#181b24; --ink:#e6e8ee; --muted:#9aa3b2;
           --accent:#5aa9e6; --line:#2a2f3a; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
          font-family:-apple-system,Segoe UI,Roboto,sans-serif; line-height:1.5; }}
  header {{ padding:32px 24px; border-bottom:1px solid var(--line); }}
  h1 {{ margin:0 0 4px; font-size:26px; }}
  .sub {{ color:var(--muted); font-size:14px; }}
  main {{ max-width:1000px; margin:0 auto; padding:24px; }}
  h2 {{ margin-top:40px; border-bottom:1px solid var(--line); padding-bottom:6px; }}
  .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
            gap:12px; margin:20px 0; }}
  .card {{ background:var(--panel); border:1px solid var(--line); border-radius:10px;
           padding:16px; text-align:center; }}
  .card .v {{ font-size:22px; font-weight:700; color:var(--accent); }}
  .card .k {{ color:var(--muted); font-size:13px; margin-top:4px; }}
  figure {{ margin:20px 0; background:var(--panel); border:1px solid var(--line);
            border-radius:10px; padding:12px; }}
  figure img {{ width:100%; height:auto; border-radius:6px; }}
  figcaption {{ color:var(--muted); font-size:13px; margin-top:8px; text-align:center; }}
  table {{ width:100%; border-collapse:collapse; margin:12px 0 24px; font-size:14px;
           overflow-x:auto; display:block; }}
  th,td {{ text-align:left; padding:8px 10px; border-bottom:1px solid var(--line); }}
  th {{ color:var(--muted); font-weight:600; }}
  .badge {{ padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }}
  .badge.ok {{ background:#12351f; color:#5ce08a; }}
  .badge.bad {{ background:#3a1720; color:#ff8095; }}
</style>
</head>
<body>
<header>
  <h1>{project}</h1>
  <div class="sub">Automated analysis report · generated {generated}</div>
</header>
<main>
  <h2>Key Metrics</h2>
  <div class="cards">{kpi_cards}</div>

  <h2>Data Cleaning Summary</h2>
  <table><tr><th>Metric</th><th>Value</th></tr>{clean_rows}</table>

  <h2>Validation Results</h2>
  <table><tr><th>Gate</th><th>Check</th><th>Status</th><th>Detail</th></tr>
    {validation_rows}
  </table>

  <h2>Charts</h2>
  {charts}

  <h2>Key Tables</h2>
  {tables}
</main>
</body>
</html>"""
