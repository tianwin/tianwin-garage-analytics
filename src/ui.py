"""Streamlit presentation layer for the analytics case study."""

from __future__ import annotations

import pandas as pd
import streamlit as st
from streamlit_echarts import st_echarts

from src import charts
from src.config import DATASET_LABEL, SQL_DIR, reliability_label
from src.database import initialize_database, run_sql_file
from src.insights import (
    customer_concentration_insight,
    repeat_customer_insight,
    revenue_interpretation,
    revenue_trend_insight,
    service_mix_insight,
)
from src.metrics import summary_metrics
from src.recommendations import generate_recommendations


def _currency(value: float) -> str:
    return f"${value:,.0f}"


def _filtered(orders: pd.DataFrame, selection: str) -> pd.DataFrame:
    if orders.empty or selection == "All History":
        return orders.copy()
    dated = orders.dropna(subset=["order_date"])
    if selection == "Year to Date":
        return dated[dated["order_date"].dt.year.eq(dated["order_date"].dt.year.max())].copy()
    weeks = 4 if selection == "Last 4 Active Weeks" else 12
    active = sorted(dated.loc[dated["is_paid"], "week_start"].dropna().unique())
    selected = set(active[-weeks:])
    return dated[dated["week_start"].isin(selected)].copy()


def _marts(orders: pd.DataFrame) -> dict[str, pd.DataFrame]:
    connection = initialize_database(orders)
    return {
        name: run_sql_file(connection, SQL_DIR / file)
        for name, file in {
            "weekly": "01_weekly_kpis.sql",
            "service": "02_service_performance.sql",
            "customer": "03_customer_metrics.sql",
            "payment": "04_payment_summary.sql",
            "daily": "05_daily_revenue.sql",
        }.items()
    }


def _quality(orders: pd.DataFrame) -> pd.DataFrame:
    connection = initialize_database(orders)
    frame = run_sql_file(connection, SQL_DIR / "06_data_quality.sql")
    frame["coverage_pct"] = frame["valid_records"].div(frame["eligible_records"]).fillna(0).mul(100)
    frame["reliability"] = frame["coverage_pct"].map(reliability_label)
    return frame


def _hero(orders: pd.DataFrame) -> None:
    dates = orders["order_date"].dropna()
    scope = f"{len(orders)} orders  ·  {dates.min():%Y-%m-%d} → {dates.max():%Y-%m-%d}  ·  {orders['customer_id'].nunique()} identified customers  ·  {orders['service_category'].nunique()} service categories"
    st.markdown(
        f"<div class='hero'><p class='eyebrow'>TIANWIN GARAGE</p><h1>Operations Analytics</h1><h3>From Service Orders to Business Decisions</h3><p>An end-to-end analytics project that transforms real-world automotive service-order data into revenue, customer, service-mix, and data-quality insights.</p><div class='badges'>Python &nbsp;|&nbsp; SQL &nbsp;|&nbsp; DuckDB &nbsp;|&nbsp; Pandas &nbsp;|&nbsp; Streamlit &nbsp;|&nbsp; ECharts</div><div class='scope'>{scope}</div></div>",
        unsafe_allow_html=True,
    )


def executive_dashboard(all_orders: pd.DataFrame) -> None:
    _hero(all_orders)
    selection = st.selectbox(
        "Analysis Period", ["Last 4 Active Weeks", "Last 12 Active Weeks", "Year to Date", "All History"], index=3
    )
    orders = _filtered(all_orders, selection)
    marts = _marts(orders)
    quality = _quality(orders)
    metrics = summary_metrics(orders)
    st.caption(f"Executive analysis period: {selection} · {DATASET_LABEL}")
    st.subheader("Executive Summary")
    insights = [
        revenue_trend_insight(marts["weekly"]),
        repeat_customer_insight(orders),
        customer_concentration_insight(orders),
        service_mix_insight(marts["service"]),
    ]
    columns = st.columns(4)
    for column, insight in zip(columns, insights, strict=True):
        column.markdown(
            f"<div class='insight'><b>{insight.title}</b><p>{insight.statement}</p><span>{insight.metric}</span></div>",
            unsafe_allow_html=True,
        )
    cols = st.columns(4)
    for col, label, value in zip(
        cols,
        ["Collected Revenue", "Paid Orders", "Average Ticket", "Repeat Customer Revenue"],
        [
            _currency(metrics["collected_revenue"]),
            f"{metrics['paid_orders']:,}",
            _currency(metrics["average_ticket"]),
            f"{metrics['repeat_revenue_share']:.1%}",
        ],
        strict=True,
    ):
        col.metric(label, value)
    st.caption(
        f"Recorded Contribution: {_currency(metrics['recorded_contribution'])}  ·  Top-5 Customer Revenue: {metrics['top_five_share']:.1%}  ·  Part Cost Coverage: {metrics['part_cost_coverage']:.1%}  ·  Identified Customers: {metrics['identified_customers']}"
    )
    st.subheader("Revenue Performance")
    st_echarts(charts.weekly_performance(marts["weekly"]), height="470px", theme="streamlit", key=f"weekly-{selection}")
    st.info(revenue_interpretation(marts["weekly"]), icon="ℹ️")
    left, right = st.columns([1.45, 1])
    with left:
        st.subheader("Service Performance")
        st_echarts(
            charts.horizontal_bars(marts["service"], "service_category", "collected_revenue"),
            height="410px",
            theme="streamlit",
            key=f"service-{selection}",
        )
    with right:
        st.subheader("Service Leaders")
        if not marts["service"].empty:
            service = marts["service"]
            st.metric("Highest Revenue Service", service.loc[service["collected_revenue"].idxmax(), "service_category"])
            st.metric("Most Frequent Service", service.loc[service["orders"].idxmax(), "service_category"])
            st.metric("Highest Average Ticket", service.loc[service["average_ticket"].idxmax(), "service_category"])
            st.caption(
                "Recorded contribution is not used to label a service as profitable because cost coverage is incomplete."
            )
    st.subheader("Customer Concentration")
    st_echarts(charts.customer_pareto(marts["customer"]), height="420px", theme="streamlit", key=f"pareto-{selection}")
    a, b, c = st.columns(3)
    a.metric("Repeat Customer Revenue", f"{metrics['repeat_revenue_share']:.1%}")
    b.metric("Top-5 Customer Revenue", f"{metrics['top_five_share']:.1%}")
    c.metric("Repeat Customer Count", metrics["repeat_customer_count"])
    st.subheader("Daily Revenue Calendar")
    years = sorted(pd.to_datetime(marts["daily"]["order_date"]).dt.year.unique(), reverse=True)
    if years:
        year = st.selectbox("Calendar year", years)
        st_echarts(
            charts.revenue_calendar(marts["daily"], int(year)),
            height="260px",
            theme="streamlit",
            key=f"calendar-{year}-{selection}",
        )
    left, right = st.columns(2)
    with left:
        st.subheader("Payment Mix")
        st_echarts(
            charts.horizontal_bars(marts["payment"], "payment_method", "collected_revenue"),
            height="310px",
            theme="streamlit",
            key=f"payment-{selection}",
        )
    with right:
        st.subheader("Recorded Contribution")
        st.metric("Recorded Gross Contribution", _currency(metrics["recorded_contribution"]))
        st.warning(
            "Based on available historical part-cost records. This is not net profit and excludes labor cost, fuel, taxes, insurance, tools, depreciation, and overhead."
        )
    st.subheader("Data Reliability")
    st_echarts(charts.quality_coverage(quality), height="370px", theme="streamlit", key=f"quality-{selection}")
    st.dataframe(
        quality.assign(coverage_pct=quality["coverage_pct"].map(lambda x: f"{x:.1f}%")),
        hide_index=True,
        width="stretch",
    )
    st.subheader("Business Recommendations")
    for recommendation in generate_recommendations(metrics, marts["service"], quality):
        st.markdown(f"**{recommendation.title}**  \n{recommendation.action}  \n*Evidence: {recommendation.rationale}*")


def analysis_page(orders: pd.DataFrame) -> None:
    st.title("Analysis")
    st.caption("Deeper inspection of privacy-safe analytical aggregates.")
    marts = _marts(orders)
    quality = _quality(orders)
    weekly = marts["weekly"].copy()
    monthly = (
        orders.assign(month=orders["order_date"].dt.to_period("M").astype(str))
        .groupby("month", as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            collected_revenue=("total_price", lambda s: s[orders.loc[s.index, "is_paid"]].sum()),
            average_ticket=("total_price", lambda s: s[orders.loc[s.index, "is_paid"]].mean()),
        )
    )
    st.header("Revenue")
    st.dataframe(weekly, hide_index=True, width="stretch")
    st.dataframe(monthly, hide_index=True, width="stretch")
    st.download_button("Download weekly aggregate CSV", weekly.to_csv(index=False), "weekly_kpis.csv", "text/csv")
    st.header("Services")
    service = marts["service"].copy()
    service["revenue_share"] = service["collected_revenue"].div(service["collected_revenue"].sum()).fillna(0)
    st.dataframe(service, hide_index=True, width="stretch")
    st.header("Customers")
    customer = marts["customer"].copy()
    customer["average_ticket"] = customer["collected_revenue"].div(customer["orders"]).fillna(0)
    customer["repeat_customer"] = customer["orders"] >= 2
    st.dataframe(customer, hide_index=True, width="stretch")
    st.header("Payments")
    st.dataframe(marts["payment"], hide_index=True, width="stretch")
    st.header("Data Quality")
    st.dataframe(quality, hide_index=True, width="stretch")


def methodology_page() -> None:
    st.title("Methodology")
    st.header("Business Problem")
    st.write(
        "The business had service-order records but no standardized way to measure revenue performance, understand repeat customers, compare service categories, or assess whether the data was reliable enough for decisions."
    )
    st.header("Data Source")
    st.info(
        "This portfolio uses anonymized operational service records. Personally identifiable information has been removed."
    )
    st.header("Pipeline")
    st.code(
        "Operational Orders\n      ↓\nPrivacy / Anonymization\n      ↓\nSchema Validation\n      ↓\nCleaning & Normalization\n      ↓\nDuckDB → SQL Analytical Marts\n      ↓\nKPI & Insight Layer\n      ↓\nStreamlit + ECharts\n      ↓\nBusiness Decisions",
        language=None,
    )
    st.header("KPI Definitions")
    st.markdown(
        "**Collected Revenue:** total price from paid orders.  \n**Average Ticket:** collected revenue / paid orders.  \n**Recorded Gross Contribution:** collected revenue − recorded part cost; never net profit.  \n**Repeat Customer:** identified customer with two or more orders."
    )
    st.header("Data Challenges")
    st.write(
        "Inconsistent payment labels, free-text services, incomplete part costs, sparse labor hours, missing customer identifiers, and inconsistent vehicle naming required explicit cleaning and validation."
    )
    st.header("Analytical Decisions")
    st.warning(
        "Labor efficiency, hourly demand, vehicle-make profitability, margin distributions, geography, conversion funnels, parts status, true operating profit, and net profit are intentionally excluded until the required fields meet reliability thresholds."
    )
    st.header("Limitations")
    st.write(
        "Contribution is not profit; cost and labor coverage are incomplete; classifications are rule-based; unidentified customers are excluded from customer KPIs; the sample represents one small growing business; all relationships are descriptive, not causal."
    )


def render_app(orders: pd.DataFrame) -> None:
    tabs = st.tabs(["Executive Dashboard", "Analysis", "Methodology"])
    with tabs[0]:
        executive_dashboard(orders)
    with tabs[1]:
        analysis_page(orders)
    with tabs[2]:
        methodology_page()
    st.markdown(
        "<div class='footer'>Built by Frank Dong<br/>Python · SQL · DuckDB · Streamlit · ECharts</div>",
        unsafe_allow_html=True,
    )
