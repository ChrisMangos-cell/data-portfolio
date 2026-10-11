import os
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# Configuration & Page Setup
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Commercial Revenue & Retention Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling: Prevents metric ellipsis truncation and sharpens layout
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 0.85rem 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.55rem !important;
        font-weight: 700 !important;
        white-space: nowrap !important;
        overflow: visible !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #4a5568 !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loading (Cached)
# -----------------------------------------------------------------------------
@st.cache_data
def load_analytics_data():
    base_path = Path(__file__).resolve().parent.parent / "data_exports"
    
    # Fallback if running from repository root
    if not base_path.exists():
        base_path = Path("sales_customer_analytics/data_exports")
        
    cohort_df = pd.read_parquet(base_path / "cohort_retention.parquet")
    rfm_df = pd.read_parquet(base_path / "rfm_segments.parquet")
    pareto_df = pd.read_parquet(base_path / "pareto_revenue.parquet")
    
    return cohort_df, rfm_df, pareto_df

try:
    cohort_df, rfm_df, pareto_df = load_analytics_data()
except Exception as e:
    st.error(f"Error loading analytical data: {e}. Ensure Parquet exports exist in 'sales_customer_analytics/data_exports/'.")
    st.stop()

# Helper for formatted currency display
def format_currency(val: float) -> str:
    if val >= 1_000_000:
        return f"R$ {val / 1_000_000:.2f}M"
    elif val >= 1_000:
        return f"R$ {val / 1_000:.1f}k"
    return f"R$ {val:.2f}"

# -----------------------------------------------------------------------------
# Sidebar Navigation & Global Metrics
# -----------------------------------------------------------------------------
st.sidebar.title("Navigation & Filters")
st.sidebar.markdown("---")

total_gmv = pareto_df["total_gross_value"].sum()
total_unique_customers = len(rfm_df)
dormant_gmv = rfm_df[rfm_df["customer_segment"].isin(["Dormant Big Spenders", "At-Risk High-Value"])]["monetary_value"].sum()

st.sidebar.metric("Total Marketplace GMV", format_currency(total_gmv))
st.sidebar.metric("Unique Customer Base", f"{total_unique_customers:,}")
st.sidebar.metric("At-Risk / Dormant GMV", format_currency(dormant_gmv))
st.sidebar.markdown("---")
st.sidebar.caption("Portfolio Project: 100k+ Transactions Analysis (DuckDB + SQL + Streamlit)")

# Header
st.title("E-Commerce Revenue, Retention & Customer Risk Engine")
st.markdown("Commercial analytics platform diagnosing customer churn velocity, RFM revenue concentration, and SKU pareto distribution.")

# -----------------------------------------------------------------------------
# Tabs Interface
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📈 Cohort Retention Dynamics", 
    "🎯 RFM Segmentation & Risk", 
    "📦 Category Pareto Distribution"
])

# =============================================================================
# TAB 1: Cohort Retention Dynamics
# =============================================================================
with tab1:
    st.subheader("Monthly Acquisition Cohort Retention (Months 1–12)")
    st.markdown(
        "Evaluates the speed of customer decay. **Key Insight:** Repeat retention drops below 0.7% by Month 1 across all cohorts, "
        "confirming an acquisition-dependent business model lacking compounding repeat loops."
    )
    
    col1, col2 = st.columns([3, 1])
    with col2:
        hide_month_0 = st.checkbox("Hide Month 0 (100% Baseline)", value=True, help="Removes Month 0 to reveal high-contrast retention variance.")
        max_period = st.slider("Max Period Index (Months)", min_value=3, max_value=12, value=12)

    cohort_df["cohort_month_str"] = pd.to_datetime(cohort_df["cohort_month"]).dt.strftime("%Y-%m")
    filtered_cohort = cohort_df[cohort_df["period_index"] <= max_period]
    
    pivot_matrix = filtered_cohort.pivot(
        index="cohort_month_str",
        columns="period_index",
        values="retention_rate_pct"
    )
    
    if hide_month_0 and 0 in pivot_matrix.columns:
        pivot_matrix = pivot_matrix.drop(columns=[0])

    fig_heat = px.imshow(
        pivot_matrix,
        labels=dict(x="Months Since First Purchase", y="Acquisition Cohort", color="Retention %"),
        x=[f"Month {c}" for c in pivot_matrix.columns],
        y=pivot_matrix.index,
        color_continuous_scale="Blues",
        aspect="auto",
        text_auto=".2f"
    )
    fig_heat.update_layout(height=520, margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_heat, use_container_width=True)

# =============================================================================
# TAB 2: RFM Customer Segmentation & Risk (Optimized Clarity)
# =============================================================================
with tab2:
    st.subheader("Behavioral Customer Segmentation & Revenue Decoupling")
    st.markdown(
        "Compare customer headcount against realized revenue. **Key Takeaway:** The **Dormant Big Spenders** and **At-Risk High-Value** "
        "segments capture a disproportionate share of historical GMV, making them prime targets for automated win-back marketing."
    )
    
    # Filter selection
    all_segments = rfm_df["customer_segment"].unique().tolist()
    selected_segments = st.multiselect(
        "Filter Customer Segments",
        options=all_segments,
        default=all_segments
    )
    
    filtered_rfm = rfm_df[rfm_df["customer_segment"].isin(selected_segments)]
    
    # Clean KPI Row with Adaptive Number Formatting
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    filt_count = len(filtered_rfm)
    filt_rev = filtered_rfm["monetary_value"].sum()
    filt_med = filtered_rfm["monetary_value"].median()
    filt_rec = filtered_rfm["recency_days"].mean()
    
    kpi1.metric("Selected Customers", f"{filt_count:,}")
    kpi2.metric("Realized Revenue", format_currency(filt_rev))
    kpi3.metric("Median Spend", format_currency(filt_med))
    kpi4.metric("Avg Inactivity", f"{filt_rec:.0f} days" if not np.isnan(filt_rec) else "N/A")
    
    st.markdown("---")
    
    if filt_count > 0:
        # Segment Aggregation
        summary = filtered_rfm.groupby("customer_segment").agg(
            customers=("customer_unique_id", "count"),
            total_revenue=("monetary_value", "sum"),
            avg_recency=("recency_days", "mean"),
            median_spend=("monetary_value", "median")
        ).reset_index().sort_values(by="total_revenue", ascending=False)
        
        summary["pct_customers"] = (summary["customers"] / len(rfm_df)) * 100
        summary["pct_revenue"] = (summary["total_revenue"] / total_gmv) * 100
        
        # Color coding: Crimson for At-Risk / Dormant, Blue for others
        colors = ["#e53e3e" if ("At-Risk" in s or "Dormant" in s) else "#3182ce" for s in summary["customer_segment"]]
        
        col_chart_left, col_chart_right = st.columns(2)
        
        with col_chart_left:
            st.markdown("##### 👥 Customer Volume by Segment")
            fig_cust = px.bar(
                summary,
                x="customer_segment",
                y="customers",
                text=summary["customers"].apply(lambda x: f"{x:,}"),
                color="customer_segment",
                color_discrete_sequence=colors
            )
            fig_cust.update_traces(textposition="outside")
            fig_cust.update_layout(
                showlegend=False,
                xaxis_title="",
                yaxis_title="Total Customers",
                height=380,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_cust, use_container_width=True)
            
        with col_chart_right:
            st.markdown("##### 💰 Realized GMV by Segment (R$)")
            fig_rev = px.bar(
                summary,
                x="customer_segment",
                y="total_revenue",
                text=summary["total_revenue"].apply(lambda x: format_currency(x)),
                color="customer_segment",
                color_discrete_sequence=colors
            )
            fig_rev.update_traces(textposition="outside")
            fig_rev.update_layout(
                showlegend=False,
                xaxis_title="",
                yaxis_title="Total GMV (R$)",
                height=380,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_rev, use_container_width=True)

        with st.expander("📊 Segment Commercial Breakdown Table"):
            display_summary = summary.copy()
            display_summary["total_revenue"] = display_summary["total_revenue"].apply(format_currency)
            display_summary["median_spend"] = display_summary["median_spend"].apply(format_currency)
            display_summary["pct_customers"] = display_summary["pct_customers"].map("{:.1f}%".format)
            display_summary["pct_revenue"] = display_summary["pct_revenue"].map("{:.1f}%".format)
            display_summary["avg_recency"] = display_summary["avg_recency"].map("{:.0f} days".format)
            display_summary.columns = ["Segment", "Customers", "Total GMV", "Avg Inactivity", "Median Spend", "Share of Users", "Share of GMV"]
            st.dataframe(display_summary, use_container_width=True)

        with st.expander("🔍 Customer Drill-Down Table (Top 100 Accounts)"):
            st.dataframe(
                filtered_rfm[["customer_unique_id", "customer_segment", "recency_days", "frequency", "monetary_value", "r_score", "f_score", "m_score"]].head(100),
                use_container_width=True
            )
            csv_data = filtered_rfm.to_csv(index=False).encode("utf-8")
            st.download_button("Download Filtered Segment Data (CSV)", data=csv_data, file_name="rfm_filtered_customers.csv", mime="text/csv")
    else:
        st.warning("Select at least one customer segment above to display analytics.")

# =============================================================================
# TAB 3: Category Pareto & Concentration
# =============================================================================
with tab3:
    st.subheader("Catalog Revenue Concentration (Pareto Analysis)")
    pareto_threshold = st.slider("Target Revenue Cutoff (%)", min_value=50, max_value=95, value=80, step=5)
    
    pareto_sorted = pareto_df.sort_values(by="total_gross_value", ascending=False).reset_index(drop=True)
    pareto_sorted["category_rank"] = np.arange(1, len(pareto_sorted) + 1)
    
    core_cats = pareto_sorted[pareto_sorted["cumulative_revenue_pct"] <= pareto_threshold]
    core_count = len(core_cats)
    total_cats = len(pareto_sorted)
    core_pct = (core_count / total_cats) * 100
    
    st.info(f"**Commercial Finding:** Exactly **{core_count} out of {total_cats} categories ({core_pct:.1f}%)** generate the first **{pareto_threshold}%** of total marketplace revenue.")
    
    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Scatter(
        x=pareto_sorted["category_rank"],
        y=pareto_sorted["cumulative_revenue_pct"],
        mode="lines",
        name="Cumulative Revenue %",
        line=dict(color="#38a169", width=3)
    ))
    fig_pareto.add_hline(y=pareto_threshold, line_dash="dash", line_color="#e53e3e", annotation_text=f"{pareto_threshold}% Target")
    fig_pareto.add_vline(x=core_count, line_dash="dot", line_color="#718096", annotation_text=f"{core_count} Categories")
    
    fig_pareto.update_layout(
        xaxis_title="Category Rank (Ordered by Revenue)",
        yaxis_title="Cumulative Gross Revenue (%)",
        height=450,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_pareto, use_container_width=True)
    
    st.write(f"### Top {core_count} Core Categories Driving {pareto_threshold}% GMV")
    st.dataframe(
        core_cats[["category_rank", "category_name", "total_orders", "total_units_sold", "total_gross_value", "pct_of_total_revenue", "cumulative_revenue_pct"]],
        use_container_width=True
    )
