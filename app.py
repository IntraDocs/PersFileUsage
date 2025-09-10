# app.py
import streamlit as st
import polars as pl
import altair as alt
from pathlib import Path

st.set_page_config(page_title="Personnel File Portal — Analytics Dashboard", layout="wide")
st.title("Personnel File Portal — Analytics Dashboard")

# Load data
csv_path = Path("out/user_agents.csv")
hourly_path = Path("out/hourly_active_users.csv")
daily_path = Path("out/daily_active_users.csv")
peak_hours_path = Path("out/peak_hours_analysis.csv")

# Check if core data exists
if not csv_path.exists():
    st.info("No user agent data yet. Run the VS Code task **Run UA analysis** first.")
    st.stop()

# Load user agent data
df = pl.read_csv(csv_path)

# Load activity data if available
hourly_df = None
daily_df = None
peak_hours_df = None

if hourly_path.exists():
    hourly_df = pl.read_csv(hourly_path)
if daily_path.exists():
    daily_df = pl.read_csv(daily_path)
if peak_hours_path.exists():
    peak_hours_df = pl.read_csv(peak_hours_path)

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["User Agents", "Active Users", "Peak Hours Analysis"])

with tab1:
    st.header("Browser & Device Analysis")
    
    # Sidebar filters for user agents
    dates = sorted(df["date"].unique().to_list()) if df.height > 0 else []
    sel_dates = st.sidebar.multiselect("Date", dates, default=dates)
    browser_filter = st.sidebar.text_input("Browser contains (optional)")

    f = df
    if sel_dates:
        f = f.filter(pl.col("date").is_in(sel_dates))
    if browser_filter:
        f = f.filter(pl.col("browser").str.contains(browser_filter, literal=False, case=False))

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Unique users", f["user_id"].n_unique() if f.height else 0)
    col2.metric("Browsers", f["browser"].n_unique() if f.height else 0)
    col3.metric("Operating Systems", f["os"].n_unique() if f.height else 0)

    st.subheader("Details")
    st.dataframe(f.to_pandas(), use_container_width=True)

    # Charts
    def bar_chart(df_pl: pl.DataFrame, x: str, title: str):
        if df_pl.height == 0:
            st.caption(f"No data for {title}")
            return
        g = (df_pl.group_by(x)
                   .agg(pl.n_unique("user_id").alias("users"))
                   .sort("users", descending=True))
        chart = (alt.Chart(g.to_pandas())
                   .mark_bar()
                   .encode(x=alt.X(x, sort='-y'), y="users"))
        st.subheader(title)
        st.altair_chart(chart, use_container_width=True)

    bar_chart(f, "browser", "Browsers used (unique users)")
    bar_chart(f, "os", "Operating systems (unique users)")
    bar_chart(f, "device", "Devices (unique users)")

with tab2:
    st.header("User Activity Analysis")
    
    if hourly_df is None or daily_df is None:
        st.info("No activity data yet. Run the VS Code task **Run Active Users analysis** first.")
        st.markdown("```python src/analyze_active_users.py --input logs/splits --output out```")
    else:
        # Daily activity overview
        if daily_df.height > 0:
            st.subheader("Daily Activity Overview")
            col1, col2, col3 = st.columns(3)
            
            total_unique_users = daily_df["unique_users"].sum()
            avg_daily_users = daily_df["unique_users"].mean()
            max_daily_users = daily_df["unique_users"].max()
            
            col1.metric("Total Unique Users", total_unique_users)
            col2.metric("Avg Daily Users", f"{avg_daily_users:.1f}")
            col3.metric("Peak Daily Users", max_daily_users)
            
            # Daily users chart
            daily_chart = (
                alt.Chart(daily_df.to_pandas())
                .mark_line(point=True)
                .encode(
                    x=alt.X("date:T", title="Date"),
                    y=alt.Y("unique_users:Q", title="Unique Users"),
                    tooltip=["date", "unique_users", "total_activities"]
                )
                .properties(height=300)
            )
            st.altair_chart(daily_chart, use_container_width=True)
            
            st.subheader("Daily Activity Details")
            st.dataframe(daily_df.to_pandas(), use_container_width=True)
        
        # Hourly activity heatmap
        if hourly_df.height > 0:
            st.subheader("Hourly Activity Pattern")
            
            # Create heatmap data
            heatmap_chart = (
                alt.Chart(hourly_df.to_pandas())
                .mark_rect()
                .encode(
                    x=alt.X("hour:O", title="Hour of Day"),
                    y=alt.Y("date:O", title="Date"),
                    color=alt.Color("unique_users:Q", title="Active Users", scale=alt.Scale(scheme="blues")),
                    tooltip=["date", "hour", "unique_users", "total_activities"]
                )
                .properties(height=400)
            )
            st.altair_chart(heatmap_chart, use_container_width=True)

with tab3:
    st.header("Peak Hours Analysis")
    
    if peak_hours_df is None:
        st.info("No peak hours data yet. Run the active users analysis first.")
    else:
        if peak_hours_df.height > 0:
            st.subheader("Activity by Hour (All Days Combined)")
            
            # Peak hours chart
            peak_chart = (
                alt.Chart(peak_hours_df.to_pandas())
                .mark_bar()
                .encode(
                    x=alt.X("hour:O", title="Hour of Day"),
                    y=alt.Y("avg_unique_users:Q", title="Average Unique Users"),
                    color=alt.Color("avg_unique_users:Q", scale=alt.Scale(scheme="viridis")),
                    tooltip=["hour", "avg_unique_users", "total_activities"]
                )
                .properties(height=400)
            )
            st.altair_chart(peak_chart, use_container_width=True)
            
            # Find peak hours
            if peak_hours_df.height > 0:
                peak_hour = peak_hours_df.sort("avg_unique_users", descending=True).row(0)
                quiet_hour = peak_hours_df.sort("avg_unique_users").row(0)
                
                col1, col2 = st.columns(2)
                col1.metric("Peak Hour", f"{peak_hour[0]}:00", f"{peak_hour[1]} users")
                col2.metric("Quietest Hour", f"{quiet_hour[0]}:00", f"{quiet_hour[1]} users")
            
            st.subheader("Peak Hours Details")
            st.dataframe(peak_hours_df.to_pandas(), use_container_width=True)
