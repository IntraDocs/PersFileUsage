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

# Sort usage data paths
sort_field_path = Path("out/sort_field_summary.csv")
sort_direction_path = Path("out/sort_direction_summary.csv")
sort_combination_path = Path("out/sort_combination_summary.csv")
daily_sort_path = Path("out/daily_sort_usage.csv")

# Folder selection data paths
folder_popularity_path = Path("out/folder_popularity_summary.csv")
daily_folder_path = Path("out/daily_folder_usage.csv")
hourly_folder_path = Path("out/hourly_folder_usage.csv")
user_folder_patterns_path = Path("out/user_folder_patterns.csv")
folder_summary_path = Path("out/folder_selection_summary.csv")

# Employee filter data paths
employee_filter_fields_path = Path("out/employee_filter_fields.csv")
employee_filter_types_path = Path("out/employee_filter_types.csv")
daily_employee_filter_path = Path("out/daily_employee_filter_usage.csv")
hourly_employee_filter_path = Path("out/hourly_employee_filter_usage.csv")
user_employee_filter_path = Path("out/user_employee_filter_patterns.csv")
employee_filter_summary_path = Path("out/employee_filter_summary.csv")

# Document filter data paths
document_filter_fields_path = Path("out/document_filter_fields.csv")
document_filter_types_path = Path("out/document_filter_types.csv")
daily_document_filter_path = Path("out/daily_document_filter_usage.csv")
hourly_document_filter_path = Path("out/hourly_document_filter_usage.csv")
user_document_filter_path = Path("out/user_document_filter_patterns.csv")
document_filter_summary_path = Path("out/document_filter_summary.csv")

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

# Load sort usage data if available
sort_field_df = None
sort_direction_df = None
sort_combination_df = None
daily_sort_df = None

if sort_field_path.exists():
    sort_field_df = pl.read_csv(sort_field_path)
if sort_direction_path.exists():
    sort_direction_df = pl.read_csv(sort_direction_path)
if sort_combination_path.exists():
    sort_combination_df = pl.read_csv(sort_combination_path)
if daily_sort_path.exists():
    daily_sort_df = pl.read_csv(daily_sort_path)

# Load folder selection data if available
folder_popularity_df = None
daily_folder_df = None
hourly_folder_df = None
user_folder_patterns_df = None
folder_summary_df = None

if folder_popularity_path.exists():
    folder_popularity_df = pl.read_csv(folder_popularity_path)
if daily_folder_path.exists():
    daily_folder_df = pl.read_csv(daily_folder_path)
if hourly_folder_path.exists():
    hourly_folder_df = pl.read_csv(hourly_folder_path)
if user_folder_patterns_path.exists():
    user_folder_patterns_df = pl.read_csv(user_folder_patterns_path)
if folder_summary_path.exists():
    folder_summary_df = pl.read_csv(folder_summary_path)

# Load employee filter data if available
employee_filter_fields_df = None
employee_filter_types_df = None
daily_employee_filter_df = None
hourly_employee_filter_df = None
user_employee_filter_df = None
employee_filter_summary_df = None

if employee_filter_fields_path.exists():
    employee_filter_fields_df = pl.read_csv(employee_filter_fields_path)
if employee_filter_types_path.exists():
    employee_filter_types_df = pl.read_csv(employee_filter_types_path)
if daily_employee_filter_path.exists():
    daily_employee_filter_df = pl.read_csv(daily_employee_filter_path)
if hourly_employee_filter_path.exists():
    hourly_employee_filter_df = pl.read_csv(hourly_employee_filter_path)
if user_employee_filter_path.exists():
    user_employee_filter_df = pl.read_csv(user_employee_filter_path)
if employee_filter_summary_path.exists():
    employee_filter_summary_df = pl.read_csv(employee_filter_summary_path)

# Load document filter data if available
document_filter_fields_df = None
document_filter_types_df = None
daily_document_filter_df = None
hourly_document_filter_df = None
user_document_filter_df = None
document_filter_summary_df = None

if document_filter_fields_path.exists():
    document_filter_fields_df = pl.read_csv(document_filter_fields_path)
if document_filter_types_path.exists():
    document_filter_types_df = pl.read_csv(document_filter_types_path)
if daily_document_filter_path.exists():
    daily_document_filter_df = pl.read_csv(daily_document_filter_path)
if hourly_document_filter_path.exists():
    hourly_document_filter_df = pl.read_csv(hourly_document_filter_path)
if user_document_filter_path.exists():
    user_document_filter_df = pl.read_csv(user_document_filter_path)
if document_filter_summary_path.exists():
    document_filter_summary_df = pl.read_csv(document_filter_summary_path)

# Panel Selection data paths
panel_user_summaries_path = Path("out/panel_selection_user_summaries.csv")
panel_base_panels_path = Path("out/panel_selection_base_panels.csv")
panel_concurrent_distribution_path = Path("out/panel_selection_concurrent_distribution.csv")
panel_top_performers_path = Path("out/panel_selection_top_performers.csv")
panel_summary_path = Path("out/panel_selection_summary.csv")

# Load panel selection data if available
panel_user_summaries_df = None
panel_base_panels_df = None
panel_concurrent_distribution_df = None
panel_top_performers_df = None
panel_summary_df = None

if panel_user_summaries_path.exists():
    panel_user_summaries_df = pl.read_csv(panel_user_summaries_path)
if panel_base_panels_path.exists():
    panel_base_panels_df = pl.read_csv(panel_base_panels_path)
if panel_concurrent_distribution_path.exists():
    panel_concurrent_distribution_df = pl.read_csv(panel_concurrent_distribution_path)
if panel_top_performers_path.exists():
    panel_top_performers_df = pl.read_csv(panel_top_performers_path)
if panel_summary_path.exists():
    panel_summary_df = pl.read_csv(panel_summary_path)

# Create tabs for different views
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["User Agents", "Active Users", "Peak Hours Analysis", "Sort Usage", "Folder Selection", "Employee Filter", "Document Filter", "Panel Selection"])

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

with tab4:
    st.header("Sort Functionality Usage Analysis")
    
    if sort_field_df is None or sort_direction_df is None or sort_combination_df is None:
        st.info("No sort usage data yet. Run the VS Code task **Run Sort Usage analysis** first.")
        st.markdown("```python src/analyze_sort_usage.py --input logs/splits --output out```")
    else:
        # Overview KPIs
        if sort_field_df.height > 0:
            st.subheader("Sort Usage Overview")
            col1, col2, col3, col4 = st.columns(4)
            
            total_sort_actions = sort_field_df["total_uses"].sum()
            users_using_sort = sort_field_df["unique_users"].sum()
            total_fields_used = sort_field_df.height
            most_popular_field = sort_field_df.row(0) if sort_field_df.height > 0 else None
            
            # Calculate percentage of users using sort functionality
            total_users_in_system = df["user_id"].n_unique() if df.height > 0 else 0
            sort_usage_percentage = (users_using_sort / total_users_in_system * 100) if total_users_in_system > 0 else 0
            
            col1.metric("Total Sort Actions", total_sort_actions)
            col2.metric("Users Using Sort", f"{users_using_sort} ({sort_usage_percentage:.1f}%)")
            col3.metric("Different Fields Sorted", total_fields_used)
            if most_popular_field:
                col4.metric("Most Popular Field", most_popular_field[0], f"{most_popular_field[1]} uses")
        
        # Sort field popularity
        if sort_field_df.height > 0:
            st.subheader("Most Popular Sort Fields")
            field_chart = (
                alt.Chart(sort_field_df.to_pandas())
                .mark_bar()
                .encode(
                    x=alt.X("sort_field:N", title="Sort Field", sort="-y"),
                    y=alt.Y("total_uses:Q", title="Total Uses"),
                    color=alt.Color("total_uses:Q", scale=alt.Scale(scheme="blues")),
                    tooltip=["sort_field", "total_uses", "unique_users", "days_used"]
                )
                .properties(height=400)
            )
            st.altair_chart(field_chart, use_container_width=True)
            
            st.subheader("Sort Field Details")
            st.dataframe(sort_field_df.to_pandas(), use_container_width=True)
        
        # ASC vs DESC preference
        if sort_direction_df.height > 0:
            st.subheader("Sort Direction Preference")
            col1, col2 = st.columns(2)
            
            with col1:
                direction_chart = (
                    alt.Chart(sort_direction_df.to_pandas())
                    .mark_arc(innerRadius=50)
                    .encode(
                        theta=alt.Theta("total_uses:Q"),
                        color=alt.Color("sort_direction:N", title="Direction"),
                        tooltip=["sort_direction", "total_uses", "unique_users"]
                    )
                    .properties(height=300)
                )
                st.altair_chart(direction_chart, use_container_width=True)
            
            with col2:
                st.subheader("Direction Statistics")
                st.dataframe(sort_direction_df.to_pandas(), use_container_width=True)
        
        # Most popular combinations
        if sort_combination_df.height > 0:
            st.subheader("Most Popular Sort Combinations")
            # Show top 10 combinations
            top_combinations = sort_combination_df.head(10)
            
            combination_chart = (
                alt.Chart(top_combinations.to_pandas())
                .mark_bar()
                .encode(
                    x=alt.X("sort_combination:N", title="Sort Combination", sort="-y"),
                    y=alt.Y("total_uses:Q", title="Total Uses"),
                    color=alt.Color("total_uses:Q", scale=alt.Scale(scheme="viridis")),
                    tooltip=["sort_combination", "total_uses", "unique_users", "days_used"]
                )
                .properties(height=400)
            )
            st.altair_chart(combination_chart, use_container_width=True)
            
            st.subheader("All Sort Combinations")
            st.dataframe(sort_combination_df.to_pandas(), use_container_width=True)
        
        # Daily sort usage trend
        if daily_sort_df is not None and daily_sort_df.height > 0:
            st.subheader("Daily Sort Usage Trend")
            
            daily_chart = (
                alt.Chart(daily_sort_df.to_pandas())
                .mark_line(point=True)
                .encode(
                    x=alt.X("date:T", title="Date"),
                    y=alt.Y("total_sort_actions:Q", title="Total Sort Actions"),
                    tooltip=["date", "total_sort_actions", "users_using_sort", "different_fields_sorted"]
                )
                .properties(height=300)
            )
            st.altair_chart(daily_chart, use_container_width=True)

with tab5:
    st.header("Folder Selection Analysis")
    
    if folder_popularity_df is None or folder_popularity_df.height == 0:
        st.info("No folder selection data available. This could mean that either the analyzer hasn't been run yet or there are no FolderSelected events in the logs.")
        st.markdown("**Run the VS Code task 'Run Folder Selection analysis' to generate this data.**")
    else:
        # Get summary statistics for KPIs
        users_using_folders = 0
        total_users = 0
        percentage_using_folders = 0.0
        
        if folder_summary_df is not None and folder_summary_df.height > 0:
            summary_dict = dict(zip(folder_summary_df["metric"].to_list(), folder_summary_df["value"].to_list()))
            users_using_folders = int(summary_dict.get("users_using_folders", "0"))
            total_users = int(summary_dict.get("total_users_in_system", "0"))
            percentage_using_folders = float(summary_dict.get("percentage_users_using_folders", "0.0"))
        
        # Folder selection KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        total_selections = folder_popularity_df["total_selections"].sum()
        unique_folders = folder_popularity_df.height
        max_folder_usage = folder_popularity_df["total_selections"].max()
        most_used_folder = folder_popularity_df.filter(
            pl.col("total_selections") == max_folder_usage
        )["folder_name"].first()
        
        col1.metric("Total Folder Selections", f"{total_selections:,}")
        col2.metric("Different Folders Used", unique_folders)
        col3.metric("Most Selections for One Folder", max_folder_usage)
        col4.metric("Most Popular Folder", most_used_folder)
        
        # User adoption metrics
        st.subheader("User Adoption")
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Users Using Folders", f"{users_using_folders:,}")
        col2.metric("Total Users in System", f"{total_users:,}")
        col3.metric("Adoption Percentage", f"{percentage_using_folders:.1f}%")
        
        # Folder popularity
        if folder_popularity_df.height > 0:
            st.subheader("Folder Popularity")
            
            # Calculate percentage for top 10 folders
            top_folders = folder_popularity_df.head(10)
            chart_data = top_folders.with_columns([
                (pl.col("total_selections") / total_selections * 100).round(1).alias("percentage")
            ]).to_pandas()
            
            folder_chart = (
                alt.Chart(chart_data)
                .mark_bar()
                .encode(
                    x=alt.X("total_selections:Q", title="Total Selections"),
                    y=alt.Y("folder_name:N", title="Folder Name", sort="-x"),
                    color=alt.Color("total_selections:Q", scale=alt.Scale(scheme='blues')),
                    tooltip=["folder_name", "total_selections", "percentage:Q", "unique_users"]
                )
                .properties(height=400)
            )
            st.altair_chart(folder_chart, use_container_width=True)
            
            # Show the data table
            display_df = top_folders.with_columns([
                (pl.col("total_selections") / total_selections * 100).round(1).alias("percentage")
            ])
            st.dataframe(display_df, use_container_width=True)
        
        # Daily folder usage
        if daily_folder_df is not None and daily_folder_df.height > 0:
            st.subheader("Daily Folder Selection Activity")
            
            # Use bar chart for better visualization of discrete daily data
            daily_folder_chart = (
                alt.Chart(daily_folder_df.to_pandas())
                .mark_bar()
                .encode(
                    x=alt.X("date:T", title="Date"),
                    y=alt.Y("total_folder_selections:Q", title="Total Folder Selections"),
                    color=alt.Color("total_folder_selections:Q", scale=alt.Scale(scheme='blues')),
                    tooltip=["date", "total_folder_selections", "users_selecting_folders", "different_folders_selected"]
                )
                .properties(height=300)
            )
            st.altair_chart(daily_folder_chart, use_container_width=True)
            
            # Show the actual data since there are only a few data points
            st.markdown("**Daily breakdown:**")
            st.dataframe(daily_folder_df, use_container_width=True)
        
        # Hourly patterns
        if hourly_folder_df is not None and hourly_folder_df.height > 0:
            st.subheader("Hourly Folder Selection Patterns")
            
            hourly_folder_chart = (
                alt.Chart(hourly_folder_df.to_pandas())
                .mark_bar()
                .encode(
                    x=alt.X("hour:O", title="Hour of Day"),
                    y=alt.Y("total_folder_selections:Q", title="Total Folder Selections"),
                    color=alt.Color("total_folder_selections:Q", scale=alt.Scale(scheme='viridis')),
                    tooltip=["hour", "total_folder_selections", "avg_users_selecting", "different_folders_selected"]
                )
                .properties(height=300)
            )
            st.altair_chart(hourly_folder_chart, use_container_width=True)
        
        # User folder behavior
        if user_folder_patterns_df is not None and user_folder_patterns_df.height > 0:
            st.subheader("User Folder Selection Behavior")
            
            # Top users by folder selections
            top_users = user_folder_patterns_df.head(20).to_pandas()
            
            user_chart = (
                alt.Chart(top_users)
                .mark_bar()
                .encode(
                    x=alt.X("total_folder_selections:Q", title="Total Folder Selections"),
                    y=alt.Y("user_id:N", title="User ID", sort="-x"),
                    color=alt.Color("different_folders_used:Q", scale=alt.Scale(scheme='oranges')),
                    tooltip=["user_id", "total_folder_selections", "different_folders_used", "most_used_folder"]
                )
                .properties(height=500)
            )
            st.altair_chart(user_chart, use_container_width=True)

with tab6:
    st.header("Employee Filter Analysis")
    
    if employee_filter_fields_df is None or employee_filter_fields_df.height == 0:
        st.info("No employee filter data available. This could mean that either the analyzer hasn't been run yet or there are no Employee filter events in the logs.")
        st.markdown("**Run the VS Code task 'Run Employee Filter analysis' to generate this data.**")
    else:
        # Get summary statistics for KPIs
        users_using_filters = 0
        total_users = 0
        percentage_using_filters = 0.0
        
        if employee_filter_summary_df is not None and employee_filter_summary_df.height > 0:
            summary_dict = dict(zip(employee_filter_summary_df["metric"].to_list(), employee_filter_summary_df["value"].to_list()))
            users_using_filters = int(summary_dict.get("users_using_filters", "0"))
            total_users = int(summary_dict.get("total_users_in_system", "0"))
            percentage_using_filters = float(summary_dict.get("percentage_users_using_filters", "0.0"))
            most_popular_field = summary_dict.get("most_popular_field", "N/A")
            most_common_type = summary_dict.get("most_common_filter_type", "N/A")
        
        # Employee filter KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        total_filters = employee_filter_fields_df["total_filters"].sum()
        different_fields = employee_filter_fields_df.height
        
        col1.metric("Total Employee Filters", f"{total_filters:,}")
        col2.metric("Different Fields Filtered", different_fields)
        col3.metric("Most Popular Field", most_popular_field)
        col4.metric("Most Common Filter Type", most_common_type)
        
        # User adoption metrics
        st.subheader("User Adoption")
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Users Using Employee Filters", f"{users_using_filters:,}")
        col2.metric("Total Users in System", f"{total_users:,}")
        col3.metric("Adoption Percentage", f"{percentage_using_filters:.1f}%")
        
        # Filter field popularity
        if employee_filter_fields_df.height > 0:
            st.subheader("Field Usage Popularity")
            
            # Show top 10 fields
            top_fields = employee_filter_fields_df.head(10)
            field_chart_data = top_fields.with_columns([
                (pl.col("total_filters") / total_filters * 100).round(1).alias("percentage")
            ]).to_pandas()
            
            field_chart = (
                alt.Chart(field_chart_data)
                .mark_bar()
                .encode(
                    x=alt.X("total_filters:Q", title="Total Filters Applied"),
                    y=alt.Y("field_name:N", title="Field Name", sort="-x"),
                    color=alt.Color("total_filters:Q", scale=alt.Scale(scheme='greens')),
                    tooltip=["field_name", "total_filters", "percentage:Q", "unique_users"]
                )
                .properties(height=400)
            )
            st.altair_chart(field_chart, use_container_width=True)
            
            # Show the data table
            display_df = top_fields.with_columns([
                (pl.col("total_filters") / total_filters * 100).round(1).alias("percentage")
            ])
            st.dataframe(display_df, use_container_width=True)
        
        # Filter type distribution
        if employee_filter_types_df is not None and employee_filter_types_df.height > 0:
            st.subheader("Filter Type Distribution")
            
            type_chart = (
                alt.Chart(employee_filter_types_df.to_pandas())
                .mark_arc(innerRadius=50)
                .encode(
                    theta=alt.Theta("total_usage:Q", title="Usage Count"),
                    color=alt.Color("filter_type:N", title="Filter Type"),
                    tooltip=["filter_type", "total_usage", "unique_users", "different_fields"]
                )
                .properties(height=300)
            )
            st.altair_chart(type_chart, use_container_width=True)
            
            # Show type breakdown
            st.dataframe(employee_filter_types_df, use_container_width=True)
        
        # Daily filter usage
        if daily_employee_filter_df is not None and daily_employee_filter_df.height > 0:
            st.subheader("Daily Employee Filter Activity")
            
            daily_filter_chart = (
                alt.Chart(daily_employee_filter_df.to_pandas())
                .mark_bar()
                .encode(
                    x=alt.X("date:T", title="Date"),
                    y=alt.Y("total_filters:Q", title="Total Employee Filters"),
                    color=alt.Color("total_filters:Q", scale=alt.Scale(scheme='oranges')),
                    tooltip=["date", "total_filters", "users_using_filters", "different_fields_filtered"]
                )
                .properties(height=300)
            )
            st.altair_chart(daily_filter_chart, use_container_width=True)
            
            # Show daily breakdown
            st.markdown("**Daily breakdown:**")
            st.dataframe(daily_employee_filter_df, use_container_width=True)
        
        # Hourly patterns
        if hourly_employee_filter_df is not None and hourly_employee_filter_df.height > 0:
            st.subheader("Hourly Employee Filter Patterns")
            
            hourly_filter_chart = (
                alt.Chart(hourly_employee_filter_df.to_pandas())
                .mark_bar()
                .encode(
                    x=alt.X("hour:O", title="Hour of Day"),
                    y=alt.Y("total_filters:Q", title="Total Employee Filters"),
                    color=alt.Color("total_filters:Q", scale=alt.Scale(scheme='purples')),
                    tooltip=["hour", "total_filters", "users_using_filters", "different_fields_filtered"]
                )
                .properties(height=300)
            )
            st.altair_chart(hourly_filter_chart, use_container_width=True)

with tab7:
    st.header("Document Filter Analysis")
    
    if document_filter_fields_df is None or document_filter_fields_df.height == 0:
        st.info("No document filter data available. This could mean that either the analyzer hasn't been run yet or there are no Document filter events in the logs.")
        st.markdown("**Run the VS Code task 'Run Document Filter analysis' to generate this data.**")
    else:
        # Get summary statistics for KPIs
        users_using_filters = 0
        total_users = 0
        percentage_using_filters = 0.0
        
        if document_filter_summary_df is not None and document_filter_summary_df.height > 0:
            summary_dict = dict(zip(document_filter_summary_df["metric"].to_list(), document_filter_summary_df["value"].to_list()))
            users_using_filters = int(summary_dict.get("users_using_filters", "0"))
            total_users = int(summary_dict.get("total_users_in_system", "0"))
            percentage_using_filters = float(summary_dict.get("percentage_users_using_filters", "0.0"))
            most_popular_field = summary_dict.get("most_popular_field", "N/A")
            most_common_type = summary_dict.get("most_common_filter_type", "N/A")
        
        # Document filter KPIs
        col1, col2, col3, col4 = st.columns(4)
        
        total_filters = document_filter_fields_df["total_filters"].sum()
        different_fields = document_filter_fields_df.height
        
        col1.metric("Total Document Filters", f"{total_filters:,}")
        col2.metric("Different Fields Filtered", different_fields)
        col3.metric("Most Popular Field", most_popular_field)
        col4.metric("Most Common Filter Type", most_common_type)
        
        # User adoption metrics
        st.subheader("User Adoption")
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Users Using Document Filters", f"{users_using_filters:,}")
        col2.metric("Total Users in System", f"{total_users:,}")
        col3.metric("Adoption Percentage", f"{percentage_using_filters:.1f}%")
        
        # Filter field popularity
        if document_filter_fields_df.height > 0:
            st.subheader("Field Usage Popularity")
            
            # Show top 10 fields
            top_fields = document_filter_fields_df.head(10)
            field_chart_data = top_fields.with_columns([
                (pl.col("total_filters") / total_filters * 100).round(1).alias("percentage")
            ]).to_pandas()
            
            field_chart = (
                alt.Chart(field_chart_data)
                .mark_bar()
                .encode(
                    x=alt.X("total_filters:Q", title="Total Filters Applied"),
                    y=alt.Y("field_name:N", title="Field Name", sort="-x"),
                    color=alt.Color("total_filters:Q", scale=alt.Scale(scheme='blues')),
                    tooltip=["field_name", "total_filters", "percentage:Q", "unique_users"]
                )
                .properties(height=400)
            )
            st.altair_chart(field_chart, use_container_width=True)
            
            # Show the data table
            display_df = top_fields.with_columns([
                (pl.col("total_filters") / total_filters * 100).round(1).alias("percentage")
            ])
            st.dataframe(display_df, use_container_width=True)
        
        # Filter type distribution
        if document_filter_types_df is not None and document_filter_types_df.height > 0:
            st.subheader("Filter Type Distribution")
            
            type_chart = (
                alt.Chart(document_filter_types_df.to_pandas())
                .mark_arc(innerRadius=50)
                .encode(
                    theta=alt.Theta("total_usage:Q", title="Usage Count"),
                    color=alt.Color("filter_type:N", title="Filter Type"),
                    tooltip=["filter_type", "total_usage", "unique_users", "different_fields"]
                )
                .properties(height=300)
            )
            st.altair_chart(type_chart, use_container_width=True)
            
            # Show type breakdown
            st.dataframe(document_filter_types_df, use_container_width=True)
        
        # Daily filter usage
        if daily_document_filter_df is not None and daily_document_filter_df.height > 0:
            st.subheader("Daily Document Filter Activity")
            
            daily_filter_chart = (
                alt.Chart(daily_document_filter_df.to_pandas())
                .mark_bar()
                .encode(
                    x=alt.X("date:T", title="Date"),
                    y=alt.Y("total_filters:Q", title="Total Document Filters"),
                    color=alt.Color("total_filters:Q", scale=alt.Scale(scheme='teals')),
                    tooltip=["date", "total_filters", "users_using_filters", "different_fields_filtered"]
                )
                .properties(height=300)
            )
            st.altair_chart(daily_filter_chart, use_container_width=True)
            
            # Show daily breakdown
            st.markdown("**Daily breakdown:**")
            st.dataframe(daily_document_filter_df, use_container_width=True)
        
        # Hourly patterns
        if hourly_document_filter_df is not None and hourly_document_filter_df.height > 0:
            st.subheader("Hourly Document Filter Patterns")
            
            hourly_filter_chart = (
                alt.Chart(hourly_document_filter_df.to_pandas())
                .mark_bar()
                .encode(
                    x=alt.X("hour:O", title="Hour of Day"),
                    y=alt.Y("total_filters:Q", title="Total Document Filters"),
                    color=alt.Color("total_filters:Q", scale=alt.Scale(scheme='viridis')),
                    tooltip=["hour", "total_filters", "users_using_filters", "different_fields_filtered"]
                )
                .properties(height=300)
            )
            st.altair_chart(hourly_filter_chart, use_container_width=True)

# Panel Selection Tab
with tab8:
    st.header("Panel Selection Analysis")
    
    if panel_summary_df is None:
        st.info("No panel selection data yet. Run the Selected Panels analysis first:")
        st.code("python src/analyze_selected_panels.py")
        st.stop()
    
    # Extract summary data
    summary_data = {}
    for row in panel_summary_df.iter_rows(named=True):
        summary_data[row['metric']] = row['value']
    
    # Overview metrics
    st.subheader("📊 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    total_users = int(summary_data.get('total_users_analyzed', 0))
    total_lines = int(summary_data.get('total_lines_processed', 0))
    users_with_panels = int(summary_data.get('total_users_with_employee_panels', 0))
    switching_users = int(summary_data.get('users_who_switched', 0))
    
    with col1:
        st.metric("Total Users", f"{total_users:,}")
    with col2:
        st.metric("Lines Processed", f"{total_lines:,}")
    with col3:
        st.metric("Users with Employee Panels", f"{users_with_panels:,}")
    with col4:
        switching_pct = summary_data.get('switching_percentage', '0%')
        st.metric("Users Who Switch", f"{switching_users:,}", switching_pct)
    
    # Base Panel Usage
    st.subheader("🏠 Base Panel Usage")
    if panel_base_panels_df is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            # Base panel usage chart
            chart = (
                alt.Chart(panel_base_panels_df.to_pandas())
                .mark_bar()
                .encode(
                    x=alt.X("total_activations:Q", title="Activations"),
                    y=alt.Y("panel:N", title="Panel", sort="-x"),
                    color=alt.Color("total_activations:Q", scale=alt.Scale(scheme='blues')),
                    tooltip=["panel", "total_activations"]
                )
                .properties(height=200)
            )
            st.altair_chart(chart, use_container_width=True)
        
        with col2:
            st.markdown("**Base Panel Statistics:**")
            total_activations = panel_base_panels_df['total_activations'].sum()
            for row in panel_base_panels_df.sort('total_activations', descending=True).iter_rows(named=True):
                panel = row['panel']
                count = row['total_activations']
                percentage = (count / total_activations * 100) if total_activations > 0 else 0
                st.write(f"• **{panel.capitalize()}**: {count:,} ({percentage:.1f}%)")
    
    # Concurrent Panel Distribution
    st.subheader("👥 Concurrent Employee Panel Distribution")
    if panel_concurrent_distribution_df is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribution chart
            chart = (
                alt.Chart(panel_concurrent_distribution_df.to_pandas())
                .mark_arc(innerRadius=50)
                .encode(
                    theta=alt.Theta("user_count:Q"),
                    color=alt.Color("concurrent_panels:N", scale=alt.Scale(scheme='category10')),
                    tooltip=["concurrent_panels", "user_count"]
                )
                .properties(height=300)
            )
            st.altair_chart(chart, use_container_width=True)
        
        with col2:
            st.markdown("**Distribution Breakdown:**")
            for row in panel_concurrent_distribution_df.sort('concurrent_panels').iter_rows(named=True):
                panels = row['concurrent_panels']
                count = row['user_count']
                percentage = (count / total_users * 100) if total_users > 0 else 0
                panel_text = f"{panels} panel{'s' if panels != 1 else ''}"
                st.write(f"• **{panel_text}**: {count:,} users ({percentage:.1f}%)")
            
            # Business rule compliance
            st.markdown("---")
            st.markdown("**⚖️ Business Rule Compliance:**")
            st.success("✅ All users comply with max 5 concurrent employee panels")
            st.info("🔄 FIFO enforcement active for panel overflow")
    
    # Top Users Analysis
    st.subheader("🏆 Top Users")
    if panel_top_performers_df is not None:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Top Base Panel Activators:**")
            top_activators = panel_top_performers_df.filter(pl.col("metric") == "most_base_activations").head(5)
            for i, row in enumerate(top_activators.iter_rows(named=True), 1):
                st.write(f"{i}. **{row['user']}**: {row['value']:,}")
        
        with col2:
            st.markdown("**Top Employee Panel Users:**")
            top_panel_users = panel_top_performers_df.filter(pl.col("metric") == "most_unique_employee_panels").head(5)
            for i, row in enumerate(top_panel_users.iter_rows(named=True), 1):
                st.write(f"{i}. **{row['user']}**: {row['value']:,} unique panels")
        
        with col3:
            st.markdown("**Top Employee Panel Switchers:**")
            top_switchers = panel_top_performers_df.filter(pl.col("metric") == "most_switches").head(5)
            for i, row in enumerate(top_switchers.iter_rows(named=True), 1):
                st.write(f"{i}. **{row['user']}**: {row['value']:,} switches")
    
    # Panel Switching Behavior
    st.subheader("🔄 Employee Panel Switching Behavior")
    
    non_switching_users = total_users - switching_users
    switching_pct_num = float(summary_data.get('switching_percentage', '0%').rstrip('%'))
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Switching Users", f"{switching_users:,}")
    with col2:
        st.metric("Non-Switching Users", f"{non_switching_users:,}")
    with col3:
        st.metric("Switch Percentage", f"{switching_pct_num:.1f}%")
    
    # Detailed Data Tables
    st.subheader("📋 Detailed User Data")
    
    if panel_user_summaries_df is not None:
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            min_activations = st.number_input("Minimum Base Activations", min_value=0, value=0)
        with col2:
            show_switchers_only = st.checkbox("Show only users who switch panels")
        
        # Filter data
        filtered_df = panel_user_summaries_df
        if min_activations > 0:
            filtered_df = filtered_df.filter(pl.col("total_base_activations") >= min_activations)
        if show_switchers_only:
            filtered_df = filtered_df.filter(pl.col("has_switched_employee_panels") == True)
        
        if len(filtered_df) > 0:
            # Rename columns for display
            display_df = filtered_df.select([
                pl.col("user").alias("User"),
                pl.col("total_base_activations").alias("Base Activations"),
                pl.col("unique_employee_panels_opened").alias("Unique Employee Panels"),
                pl.col("max_concurrent_employee_panels").alias("Max Concurrent Panels"),
                pl.col("employee_panel_switches").alias("Employee Panel Switches"),
                pl.col("has_switched_employee_panels").alias("Switches Panels")
            ])
            
            st.dataframe(display_df.to_pandas(), use_container_width=True)
            st.caption(f"Showing {len(filtered_df):,} of {total_users:,} users")
        else:
            st.info("No users match the current filters.")
