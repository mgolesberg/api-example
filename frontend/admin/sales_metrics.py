"""
Sales Metrics Dashboard Module.

This module provides comprehensive sales analytics and reporting functionality
for administrators in the Streamlit application. It aggregates purchase data
from all users and presents it through interactive visualizations and metrics.

Key Features:
- Daily sales performance tracking with line charts
- Revenue and units sold metrics
- Top performing days analysis
- Data filtering by date ranges
- Interactive Plotly visualizations

The dashboard processes purchase data from the OrderPurchase class, cleans and
aggregates it by date, and presents comprehensive sales insights through:
- Metric cards showing totals and averages
- Dual-axis line charts for units sold and revenue
- Data tables for top performing days
- Data quality summaries

Data Processing:
- Loads purchase data from all users
- Filters data by configurable date ranges (default: 30 days)
- Aggregates daily sales metrics
- Fills missing days with zero values
- Handles timezone-aware datetime processing

Usage:
    This module is automatically loaded by the Streamlit navigation system
    when Admin users select the Sales Metrics page. The main function
    run_sales_dashboard() orchestrates the entire dashboard workflow.
"""

from datetime import datetime, timedelta, timezone

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import user_and_requests


def load_all_purchases_data():
    """
    Load and combine purchase data from all users.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing all closed purchases from all users.

    Raises
    ------
    requests.RequestException
        If any API request fails.
    """
    all_orders = {
        i: user_and_requests.OrderPurchase(i) for i in user_and_requests.get_all_users()
    }

    closed_purchases = all_orders[1].consolidate_purchases_as_datafame(False)
    for i in user_and_requests.get_all_users()[1:]:
        closed_purchases = pd.concat(
            [closed_purchases, all_orders[i].consolidate_purchases_as_datafame(False)]
        )

    return closed_purchases


def clean_and_prepare_data(closed_purchases):
    """
    Clean and prepare the raw purchase data.

    Parameters
    ----------
    closed_purchases : pd.DataFrame
        Raw purchase data DataFrame.

    Returns
    -------
    pd.DataFrame
        Cleaned and prepared purchase data with proper data types.
    """
    closed_purchases["purchase_updated_at"] = pd.to_datetime(
        closed_purchases["purchase_updated_at"], utc=True
    )
    closed_purchases["quantity"] = pd.to_numeric(
        closed_purchases["quantity"], errors="coerce"
    )
    closed_purchases["purchase_total_amount"] = pd.to_numeric(
        closed_purchases["purchase_total_amount"], errors="coerce"
    )

    return closed_purchases


def filter_by_date_range(closed_purchases, days=30):
    """
    Filter data by date range using UTC timezone.

    Parameters
    ----------
    closed_purchases : pd.DataFrame
        Purchase data DataFrame.
    days : int, optional
        Number of days to look back from current date, by default 30.

    Returns
    -------
    tuple
        A tuple containing (filtered_dataframe, start_date, end_date).
    """
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)

    closed_purchases_filtered = closed_purchases[
        (closed_purchases["purchase_updated_at"] >= start_date)
        & (closed_purchases["purchase_updated_at"] <= end_date)
    ].copy()

    return closed_purchases_filtered, start_date, end_date


def aggregate_daily_sales(closed_purchases_filtered):
    """
    Aggregate sales data by date.

    Parameters
    ----------
    closed_purchases_filtered : pd.DataFrame
        Filtered purchase data DataFrame.

    Returns
    -------
    pd.DataFrame
        Daily aggregated sales data with columns: date, units_sold, revenue, transactions.
    """
    closed_purchases_filtered["date"] = closed_purchases_filtered[
        "purchase_updated_at"
    ].dt.date

    daily_sales = (
        closed_purchases_filtered.groupby("date")
        .agg(
            {"quantity": "sum", "purchase_total_amount": "sum", "purchase_id": "count"}
        )
        .reset_index()
    )

    daily_sales.columns = ["date", "units_sold", "revenue", "transactions"]
    daily_sales["date"] = pd.to_datetime(daily_sales["date"])

    return daily_sales


def fill_missing_days(daily_sales, start_date, end_date):
    """
    Fill missing days with zero values.

    Parameters
    ----------
    daily_sales : pd.DataFrame
        Daily sales data DataFrame.
    start_date : datetime
        Start date for the complete range.
    end_date : datetime
        End date for the complete range.

    Returns
    -------
    pd.DataFrame
        Complete daily sales data with all days filled (missing days have zero values).
    """
    complete_date_range = pd.date_range(
        start=start_date.date(), end=end_date.date(), freq="D"
    )

    complete_daily_sales = pd.DataFrame({"date": complete_date_range})

    complete_daily_sales = complete_daily_sales.merge(
        daily_sales, on="date", how="left"
    ).fillna({"units_sold": 0, "revenue": 0.0, "transactions": 0})

    return complete_daily_sales


def create_metrics_cards(daily_sales):
    """
    Create and display the four metric cards in Streamlit.

    Parameters
    ----------
    daily_sales : pd.DataFrame
        Daily sales data DataFrame.
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_units = daily_sales["units_sold"].sum()
        st.metric("Total Units Sold", f"{total_units:,}")

    with col2:
        total_revenue = daily_sales["revenue"].sum()
        st.metric("Total Revenue", f"${total_revenue:,.2f}")

    with col3:
        avg_daily_units = daily_sales["units_sold"].mean()
        st.metric("Avg Daily Units", f"{avg_daily_units:.1f}")

    with col4:
        avg_daily_revenue = daily_sales["revenue"].mean()
        st.metric("Avg Daily Revenue", f"${avg_daily_revenue:,.2f}")


def create_daily_sales_chart(daily_sales):
    """
    Create the main daily sales line chart.

    Parameters
    ----------
    daily_sales : pd.DataFrame
        Daily sales data DataFrame.
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Scatter(
            x=daily_sales["date"],
            y=daily_sales["units_sold"],
            mode="lines+markers",
            name="Units Sold",
            line={"color": "#1f77b4", "width": 3},
            marker={"size": 6},
            hovertemplate="<b>Date:</b> %{x}<br><b>Units:</b> %{y:,}<extra></extra>",
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=daily_sales["date"],
            y=daily_sales["revenue"],
            mode="lines+markers",
            name="Revenue ($)",
            line={"color": "#ff7f0e", "width": 3},
            marker={"size": 6},
            hovertemplate=(
                "<b>Date:</b> %{x}<br><b>Revenue:</b> $%{y:,.2f}<extra></extra>"
            ),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title={
            "text": "Daily Sales Performance - Last 30 Days",
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20},
        },
        xaxis_title="Date",
        hovermode="x unified",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
        height=500,
        template="plotly_white",
    )

    fig.update_yaxes(title_text="<b>Units Sold</b>", secondary_y=False, color="#1f77b4")
    fig.update_yaxes(title_text="<b>Revenue ($)</b>", secondary_y=True, color="#ff7f0e")

    st.plotly_chart(fig, use_container_width=True)


def display_sales_insights(daily_sales):
    """
    Display top sales days insights.

    Parameters
    ----------
    daily_sales : pd.DataFrame
        Daily sales data DataFrame.
    """
    st.subheader("📊 Sales Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Top 5 Best Sales Days (Units)**")
        top_units_days = daily_sales.nlargest(5, "units_sold")[
            ["date", "units_sold", "revenue"]
        ]
        st.dataframe(
            top_units_days.style.format(
                {
                    "date": lambda x: x.strftime("%Y-%m-%d"),
                    "units_sold": "{:,}",
                    "revenue": "${:,.2f}",
                }
            ),
            hide_index=True,
        )

    with col2:
        st.write("**Top 5 Best Sales Days (Revenue)**")
        top_revenue_days = daily_sales.nlargest(5, "revenue")[
            ["date", "units_sold", "revenue"]
        ]
        st.dataframe(
            top_revenue_days.style.format(
                {
                    "date": lambda x: x.strftime("%Y-%m-%d"),
                    "units_sold": "{:,}",
                    "revenue": "${:,.2f}",
                }
            ),
            hide_index=True,
        )


def display_data_summary(closed_purchases, daily_sales):
    """
    Display data quality and summary information.

    Parameters
    ----------
    closed_purchases : pd.DataFrame
        Raw purchase data DataFrame.
    daily_sales : pd.DataFrame
        Daily sales data DataFrame.
    """
    with st.expander("ℹ️ About this data"):
        st.write(
            f"""
        **Data Summary:**
        - **Total Records:** {len(closed_purchases):,}
        - **Date Range:** {daily_sales['date'].min().strftime('%Y-%m-%d')} to
          {daily_sales['date'].max().strftime('%Y-%m-%d')}
        - **Total Days:** {len(daily_sales)} days
        - **Average Units/Day:** {daily_sales['units_sold'].mean():.1f}
        - **Average Revenue/Day:** ${daily_sales['revenue'].mean():,.2f}
        """
        )


def run_sales_dashboard():
    """
    Main function to run the entire sales dashboard.

    This function orchestrates the entire sales dashboard workflow:
    loading data, cleaning, filtering, aggregating, and displaying
    various charts and metrics.

    Raises
    ------
    requests.RequestException
        If any API request fails.
    """
    st.title("📈 Sales Performance Dashboard")
    st.subheader("Units Sold vs Revenue - Last 30 Days")

    closed_purchases = load_all_purchases_data()
    closed_purchases = clean_and_prepare_data(closed_purchases)
    closed_purchases_filtered, start_date, end_date = filter_by_date_range(
        closed_purchases
    )

    daily_sales = aggregate_daily_sales(closed_purchases_filtered)
    daily_sales = fill_missing_days(daily_sales, start_date, end_date)

    create_metrics_cards(daily_sales)
    create_daily_sales_chart(daily_sales)
    display_sales_insights(daily_sales)
    display_data_summary(closed_purchases, daily_sales)


if __name__ == "__main__":
    run_sales_dashboard()
