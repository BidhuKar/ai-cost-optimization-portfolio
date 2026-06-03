"""
Streamlit dashboard for the AI Cost Optimization Portfolio.
Run: streamlit run dashboard/app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="AI Cost Optimization", page_icon="💸", layout="wide")

@st.cache_data(ttl=300)
def load_data():
    path = Path(__file__).parent.parent / "data" / "raw" / "billing_data.csv"
    if not path.exists():
        st.error("Run synth_generator.py first to generate billing_data.csv")
        st.stop()
    return pd.read_csv(path, parse_dates=["timestamp"])

df = load_data()

# Sidebar filters
st.sidebar.title("🔍 Filters")
services = st.sidebar.multiselect("Service", sorted(df["service"].unique()), default=sorted(df["service"].unique()))
teams    = st.sidebar.multiselect("Team",    sorted(df["team"].unique()),    default=sorted(df["team"].unique()))
regions  = st.sidebar.multiselect("Region",  sorted(df["region"].unique()),  default=sorted(df["region"].unique()))
show_anomalies = st.sidebar.checkbox("Anomalies only", value=False)
date_min, date_max = df["timestamp"].min().date(), df["timestamp"].max().date()
date_range = st.sidebar.date_input("Date range", value=(date_min, date_max))

mask = (
    df["service"].isin(services) & df["team"].isin(teams) & df["region"].isin(regions)
    & (df["timestamp"].dt.date >= date_range[0])
    & (df["timestamp"].dt.date <= date_range[1])
)
if show_anomalies:
    mask &= df["anomaly_flag"]
fdf = df[mask]

# KPIs
st.title("💸 AI Cost Optimization Dashboard")
st.caption(f"Showing **{len(fdf):,}** records · {date_range[0]} → {date_range[1]}")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Spend",   f"${fdf['total_cost'].sum():,.2f}")
k2.metric("Records",       f"{len(fdf):,}")
k3.metric("Anomalies",     f"{fdf['anomaly_flag'].sum():,}", f"{100*fdf['anomaly_flag'].mean():.1f}%")
k4.metric("Anomaly Spend", f"${fdf.loc[fdf['anomaly_flag'],'total_cost'].sum():,.2f}")
st.divider()

col1, col2 = st.columns(2)
with col1:
    st.subheader("Daily Spend Trend")
    daily = fdf.set_index("timestamp").resample("D")["total_cost"].sum().reset_index()
    daily["rolling_7d"] = daily["total_cost"].rolling(7, min_periods=1).mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily["timestamp"], y=daily["total_cost"],
        name="Daily", fill="tozeroy", line=dict(color="steelblue", width=1), opacity=0.4))
    fig.add_trace(go.Scatter(x=daily["timestamp"], y=daily["rolling_7d"],
        name="7-day avg", line=dict(color="darkorange", width=2)))
    fig.update_layout(yaxis_tickprefix="$", height=300, margin=dict(t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Spend by Service")
    svc = fdf.groupby("service")["total_cost"].sum().reset_index().sort_values("total_cost")
    fig = px.bar(svc, x="total_cost", y="service", orientation="h",
                 color="service", color_discrete_sequence=px.colors.qualitative.Plotly,
                 labels={"total_cost":"Total Cost (USD)","service":""})
    fig.update_layout(showlegend=False, xaxis_tickprefix="$", height=300, margin=dict(t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.subheader("Spend by Team")
    tdf = fdf.groupby("team")["total_cost"].sum().reset_index()
    fig = px.pie(tdf, names="team", values="total_cost", hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(height=300, margin=dict(t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Anomaly vs Normal Spend by Service")
    adf = fdf.groupby("service").agg(
        total=("total_cost","sum"),
        anomaly=("total_cost", lambda x: x[fdf.loc[x.index,"anomaly_flag"]].sum())
    ).reset_index()
    adf["normal"] = adf["total"] - adf["anomaly"]
    fig = go.Figure()
    fig.add_bar(x=adf["service"], y=adf["normal"],  name="Normal",  marker_color="steelblue")
    fig.add_bar(x=adf["service"], y=adf["anomaly"], name="Anomaly", marker_color="tomato")
    fig.update_layout(barmode="stack", yaxis_tickprefix="$", height=300, margin=dict(t=10,b=10))
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("📋 Raw Records (latest 500)")
st.dataframe(fdf.sort_values("timestamp", ascending=False).head(500), use_container_width=True, height=300)
