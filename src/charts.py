"""ECharts option builders; no business calculations live here."""

from __future__ import annotations

import pandas as pd
from streamlit_echarts import JsCode

from src.config import PALETTE

AXIS = {"axisLine": {"lineStyle": {"color": "#CBD5E0"}}, "axisLabel": {"color": "#4A5568"}}


def weekly_performance(weekly: pd.DataFrame) -> dict:
    rows = weekly.copy()
    rows["week_start"] = pd.to_datetime(rows["week_start"]).dt.strftime("%b %d")
    return {
        "tooltip": {"trigger": "axis"},
        "legend": {"top": 0},
        "grid": {"left": 55, "right": 65, "top": 55, "bottom": 75},
        "xAxis": {"type": "category", "data": rows["week_start"].tolist(), **AXIS},
        "yAxis": [{"type": "value", "name": "USD", **AXIS}, {"type": "value", "name": "Orders", **AXIS}],
        "dataZoom": [{"type": "inside"}, {"type": "slider", "height": 20, "bottom": 20}],
        "series": [
            {
                "name": "Collected Revenue",
                "type": "bar",
                "data": rows["collected_revenue"].round(2).tolist(),
                "itemStyle": {"color": PALETTE["primary"]},
            },
            {
                "name": "Average Ticket",
                "type": "line",
                "smooth": True,
                "data": rows["average_ticket"].round(2).tolist(),
                "itemStyle": {"color": PALETTE["positive"]},
            },
            {
                "name": "Paid Orders",
                "type": "line",
                "yAxisIndex": 1,
                "data": rows["paid_orders"].tolist(),
                "itemStyle": {"color": PALETTE["warning"]},
            },
        ],
    }


def horizontal_bars(frame: pd.DataFrame, label: str, value: str, color: str | None = None) -> dict:
    rows = frame.sort_values(value)
    return {
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "grid": {"left": 125, "right": 35, "top": 10, "bottom": 35},
        "xAxis": {"type": "value", **AXIS},
        "yAxis": {"type": "category", "data": rows[label].tolist(), **AXIS},
        "series": [
            {
                "type": "bar",
                "name": value.replace("_", " ").title(),
                "data": rows[value].round(2).tolist(),
                "itemStyle": {"color": color or PALETTE["primary"], "borderRadius": [0, 3, 3, 0]},
            }
        ],
    }


def customer_pareto(customers: pd.DataFrame) -> dict:
    rows = customers.nlargest(15, "collected_revenue").copy()
    total = customers["collected_revenue"].sum()
    rows["cumulative"] = rows["collected_revenue"].cumsum().div(total).mul(100) if total else 0
    return {
        "tooltip": {"trigger": "axis"},
        "legend": {},
        "grid": {"left": 55, "right": 60, "bottom": 70},
        "xAxis": {"type": "category", "data": rows["customer_id"].tolist(), "axisLabel": {"rotate": 40}},
        "yAxis": [
            {"type": "value", "name": "Revenue", **AXIS},
            {"type": "value", "name": "Cumulative %", "max": 100, **AXIS},
        ],
        "series": [
            {
                "name": "Collected Revenue",
                "type": "bar",
                "data": rows["collected_revenue"].round(2).tolist(),
                "itemStyle": {"color": PALETTE["primary"]},
            },
            {
                "name": "Cumulative Revenue %",
                "type": "line",
                "yAxisIndex": 1,
                "data": rows["cumulative"].round(1).tolist(),
                "itemStyle": {"color": PALETTE["warning"]},
            },
        ],
    }


def revenue_calendar(daily: pd.DataFrame, year: int) -> dict:
    rows = daily[pd.to_datetime(daily["order_date"]).dt.year.eq(year)].copy()
    data = [
        [
            pd.Timestamp(row.order_date).strftime("%Y-%m-%d"),
            round(row.collected_revenue, 2),
            int(row.orders),
            round(row.cash_revenue, 2),
            round(row.zelle_revenue, 2),
            round(row.other_paid_revenue, 2),
        ]
        for row in rows.itertuples()
    ]
    maximum = max([item[1] for item in data], default=1)
    return {
        "tooltip": {
            "formatter": JsCode(
                "function(p){let d=p.data; return '<b>'+d[0]+'</b><br/>Orders: '+d[2]+'<br/>Collected Revenue: $'+d[1].toFixed(2)+'<br/>Cash: $'+d[3].toFixed(2)+'<br/>Zelle: $'+d[4].toFixed(2)+'<br/>Other Paid: $'+d[5].toFixed(2);}"
            ).js_code
        },
        "visualMap": {
            "min": 0,
            "max": maximum,
            "orient": "horizontal",
            "left": "center",
            "top": 0,
            "inRange": {"color": ["#E7EEF2", PALETTE["primary"]]},
        },
        "calendar": {
            "range": str(year),
            "top": 55,
            "left": 45,
            "right": 20,
            "cellSize": ["auto", 17],
            "itemStyle": {"borderWidth": 2, "borderColor": "#fff"},
            "yearLabel": {"show": False},
        },
        "series": [{"type": "heatmap", "coordinateSystem": "calendar", "data": data}],
    }


def quality_coverage(quality: pd.DataFrame) -> dict:
    rows = quality.sort_values("coverage_pct")
    colors = [
        PALETTE["positive"] if x >= 90 else PALETTE["warning"] if x >= 40 else PALETTE["negative"]
        for x in rows["coverage_pct"]
    ]
    data = [
        {"value": round(row.coverage_pct, 1), "itemStyle": {"color": color}}
        for row, color in zip(rows.itertuples(), colors, strict=True)
    ]
    return {
        "tooltip": {"trigger": "axis"},
        "grid": {"left": 145, "right": 55, "top": 10, "bottom": 30},
        "xAxis": {"type": "value", "max": 100, **AXIS},
        "yAxis": {"type": "category", "data": rows["field"].tolist(), **AXIS},
        "series": [{"type": "bar", "data": data, "label": {"show": True, "position": "right", "formatter": "{c}%"}}],
    }
