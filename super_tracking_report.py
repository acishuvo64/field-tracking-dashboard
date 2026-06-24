# =========================================================
# AI FIELD FORCE DASHBOARD - SHAHINUR | ACI Premio Plastics
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Field Force Dashboard",
    page_icon="📍",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 0px;
}

.sub-title {
    font-size: 16px;
    color: #64748B;
    margin-bottom: 10px;
}

.kpi-card {
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    padding: 22px;
    border-radius: 16px;
    color: white;
    text-align: center;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.15);
}

.kpi-card h4 {
    margin: 0;
    font-size: 14px;
    font-weight: 500;
    opacity: 0.85;
}

.kpi-card h2 {
    margin: 6px 0 0 0;
    font-size: 30px;
    font-weight: 800;
}

[data-testid="stSidebar"] {
    background: #0F172A;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stRadio label {
    color: white !important;
    font-weight: 600;
}

[data-testid="stSidebar"] .stSelectbox label {
    color: white !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown('<p class="main-title">📍 AI Field Force Tracking Dashboard</p>',
            unsafe_allow_html=True)
st.markdown('<p class="sub-title">ACI Premio Plastics | Professional Employee Tracking & Productivity Analytics</p>', unsafe_allow_html=True)
st.markdown("---")

# =========================================================
# LOAD DATA
# =========================================================


@st.cache_data
def load_data():
    summary = pd.read_excel("super_tracking_report.xlsx",
                            sheet_name="Summarize_data")
    image_df = pd.read_excel(
        "super_tracking_report.xlsx", sheet_name="Image_URL")
    same_place = pd.read_excel(
        "super_tracking_report.xlsx", sheet_name="SamePlace_Highest Hour")
    summary["Date"] = pd.to_datetime(summary["Date"], errors="coerce")
    same_place["Date"] = pd.to_datetime(same_place["Date"], errors="coerce")
    return summary, image_df, same_place


try:
    summary_df, image_df, same_place_df = load_data()
except Exception as e:
    st.error(f"Excel Loading Error: {e}")
    st.stop()

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.title("🎛 Dashboard Filters")

# Date range
start_date = st.sidebar.date_input("Start Date", summary_df["Date"].min())
end_date = st.sidebar.date_input("End Date", summary_df["Date"].max())

# Group filter
group_list = sorted(summary_df["Group"].dropna().unique())
selected_group = st.sidebar.selectbox("Select Group", ["All"] + group_list)

# Deg filter (RSM/TSM)
deg_list = sorted(summary_df["Deg"].dropna().unique())
selected_deg = st.sidebar.selectbox(
    "Select Designation (RSM/TSM)", ["All"] + deg_list)

# Employee filter
employee_list = sorted(summary_df["Employee Name"].dropna().unique())
selected_employee = st.sidebar.selectbox(
    "Select Employee", ["All"] + employee_list)

# =========================================================
# FILTER DATA
# =========================================================

df = summary_df.copy()

df = df[
    (df["Date"] >= pd.to_datetime(start_date)) &
    (df["Date"] <= pd.to_datetime(end_date))
]

if selected_group != "All":
    df = df[df["Group"] == selected_group]

if selected_deg != "All":
    df = df[df["Deg"] == selected_deg]

if selected_employee != "All":
    df = df[df["Employee Name"] == selected_employee]

# =========================================================
# KPI CARDS
# =========================================================

total_emp = df["Employee Name"].nunique()
total_working = round(df["Total Working Hr"].sum(), 1)
total_travel = round(df["Total Travel Hr"].sum(), 1)
total_idle = round(df["Total Idle Hr"].sum(), 1)
avg_productivity = round(df["Work productivity"].mean() * 100, 1)

c1, c2, c3, c4, c5 = st.columns(5)

kpis = [
    ("👥 Employee",       total_emp),
    ("⏱ Working Hr",     total_working),
    ("🚗 Travel Hr",     total_travel),
    ("💤 Idle Hr",       total_idle),
    ("📊 Productivity %", f"{avg_productivity}%"),
]

for col, (title, value) in zip([c1, c2, c3, c4, c5], kpis):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <h4>{title}</h4>
            <h2>{value}</h2>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# SECTION 1: EMPLOYEE DAILY BREAKDOWN PIE CHART
# =========================================================

st.subheader("🥧 Employee Hours Breakdown (Working / Travel / Idle)")

col_emp, col_mode = st.columns([2, 2])

with col_emp:
    pie_employee = st.selectbox(
        "Select Employee for Breakdown",
        employee_list,
        key="pie_emp"
    )

with col_mode:
    pie_mode = st.radio(
        "View Mode",
        ["Day Wise", "Full Month"],
        horizontal=True,
        key="pie_mode"
    )

emp_df = summary_df[
    (summary_df["Employee Name"] == pie_employee) &
    (summary_df["Date"] >= pd.to_datetime(start_date)) &
    (summary_df["Date"] <= pd.to_datetime(end_date))
].copy()

if emp_df.empty:
    st.warning("No data found for selected employee and date range.")
else:
    if pie_mode == "Day Wise":
        # Date selector for day wise
        available_dates = sorted(emp_df["Date"].dt.date.unique())
        selected_day = st.selectbox(
            "Select Date",
            available_dates,
            key="pie_date"
        )
        pie_data = emp_df[emp_df["Date"].dt.date == selected_day]
        pie_title = f"{pie_employee} — {selected_day}"
    else:
        pie_data = emp_df
        pie_title = f"{pie_employee} — Full Month"

    w_hr = round(pie_data["Total Working Hr"].sum(), 2)
    t_hr = round(pie_data["Total Travel Hr"].sum(), 2)
    i_hr = round(pie_data["Total Idle Hr"].sum(), 2)

    total_hr = w_hr + t_hr + i_hr

    if total_hr > 0:
        pie_df_chart = pd.DataFrame({
            "Category": ["Working Hr", "Travel Hr", "Idle Hr"],
            "Hours": [w_hr, t_hr, i_hr]
        })

        fig_pie = px.pie(
            pie_df_chart,
            names="Category",
            values="Hours",
            hole=0.45,
            template="plotly_dark",
            color="Category",
            color_discrete_map={
                "Working Hr": "#4F46E5",
                "Travel Hr":  "#06B6D4",
                "Idle Hr":    "#F59E0B"
            },
            title=pie_title
        )
        fig_pie.update_traces(textinfo="percent+label+value")
        fig_pie.update_layout(title_font_size=16)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("No hours data available.")

st.markdown("---")

# =========================================================
# SECTION 2: RSM vs TSM PERFORMANCE (Column Chart)
# =========================================================

st.subheader("👔 RSM vs TSM Performance Comparison")

deg_df = df.groupby(["Employee Name", "Deg"])[
    "Work productivity"].mean().reset_index()
deg_df["Work productivity"] = (deg_df["Work productivity"] * 100).round(1)
deg_df = deg_df.sort_values("Work productivity", ascending=False)

fig_deg = px.bar(
    deg_df,
    x="Employee Name",
    y="Work productivity",
    color="Deg",
    text_auto=".1f",
    barmode="group",
    template="plotly_dark",
    color_discrete_map={"RSM": "#4F46E5", "TSM": "#06B6D4"},
    title="Productivity % by Employee — Color Coded by RSM / TSM"
)
fig_deg.update_layout(
    yaxis_title="Productivity %",
    xaxis_tickangle=-45,
    legend_title="Designation"
)
st.plotly_chart(fig_deg, use_container_width=True)

st.markdown("---")

# =========================================================
# SECTION 3: TOP 10 PERFORMERS
# =========================================================

st.subheader("🏆 Top 10 Performers")

top10 = (
    df.groupby("Employee Name")["Work productivity"]
    .mean()
    .reset_index()
    .sort_values("Work productivity", ascending=False)
    .head(10)
)
top10["Work productivity"] = (top10["Work productivity"] * 100).round(1)
top10 = top10.sort_values(
    "Work productivity", ascending=True)  # for horizontal feel

fig_top = px.bar(
    top10,
    x="Work productivity",
    y="Employee Name",
    orientation="h",
    text_auto=".1f",
    template="plotly_dark",
    color="Work productivity",
    color_continuous_scale="Viridis",
    title="Top 10 Performers by Productivity %"
)
fig_top.update_layout(xaxis_title="Productivity %",
                      yaxis_title="", coloraxis_showscale=False)
st.plotly_chart(fig_top, use_container_width=True)

st.markdown("---")

# =========================================================
# SECTION 4: BOTTOM 10 PERFORMERS
# =========================================================

st.subheader("⚠️ Bottom 10 Performers")

bottom10 = (
    df.groupby("Employee Name")["Work productivity"]
    .mean()
    .reset_index()
    .sort_values("Work productivity", ascending=True)
    .head(10)
)
bottom10["Work productivity"] = (bottom10["Work productivity"] * 100).round(1)
bottom10 = bottom10.sort_values("Work productivity", ascending=False)

fig_bot = px.bar(
    bottom10,
    x="Work productivity",
    y="Employee Name",
    orientation="h",
    text_auto=".1f",
    template="plotly_dark",
    color="Work productivity",
    color_continuous_scale="Reds_r",
    title="Bottom 10 Performers by Productivity %"
)
fig_bot.update_layout(xaxis_title="Productivity %",
                      yaxis_title="", coloraxis_showscale=False)
st.plotly_chart(fig_bot, use_container_width=True)

st.markdown("---")

# =========================================================
# SECTION 5: DAILY PRODUCTIVITY TREND
# =========================================================

st.subheader("📈 Daily Productivity Trend")

daily = (
    df.groupby("Date")["Work productivity"]
    .mean()
    .reset_index()
)
daily["Work productivity"] = (daily["Work productivity"] * 100).round(1)

fig_trend = px.line(
    daily,
    x="Date",
    y="Work productivity",
    markers=True,
    template="plotly_dark",
    title="Daily Average Productivity %"
)
fig_trend.update_layout(yaxis_title="Productivity %")
st.plotly_chart(fig_trend, use_container_width=True)

st.markdown("---")

# =========================================================
# SECTION 6: WORKING vs TRAVEL vs IDLE (Group Bar)
# =========================================================

st.subheader("⚡ Working vs Travel vs Idle Hours by Employee")

compare_df = (
    df.groupby("Employee Name")[
        ["Total Working Hr", "Total Travel Hr", "Total Idle Hr"]]
    .sum()
    .reset_index()
)

fig_compare = px.bar(
    compare_df,
    x="Employee Name",
    y=["Total Working Hr", "Total Travel Hr", "Total Idle Hr"],
    barmode="group",
    template="plotly_dark",
    color_discrete_map={
        "Total Working Hr": "#4F46E5",
        "Total Travel Hr":  "#06B6D4",
        "Total Idle Hr":    "#F59E0B"
    },
    title="Hours Comparison per Employee"
)
fig_compare.update_layout(xaxis_tickangle=-45, yaxis_title="Hours")
st.plotly_chart(fig_compare, use_container_width=True)

st.markdown("---")

# =========================================================
# SECTION 7: GPS MAP
# =========================================================

st.subheader("🗺 Employee GPS Map")

if selected_employee != "All":
    map_df = df.dropna(subset=["Lat,Lon"]).copy()

    lat_list, lon_list = [], []
    for val in map_df["Lat,Lon"]:
        try:
            parts = str(val).split(",")
            lat_list.append(float(parts[0]))
            lon_list.append(float(parts[1]))
        except:
            lat_list.append(None)
            lon_list.append(None)

    map_df["Latitude"] = lat_list
    map_df["Longitude"] = lon_list
    map_df = map_df.dropna(subset=["Latitude", "Longitude"])

    if not map_df.empty:
        m = folium.Map(
            location=[map_df["Latitude"].mean(), map_df["Longitude"].mean()],
            zoom_start=10
        )
        for _, row in map_df.iterrows():
            popup_text = f"""
            <b>{row['Employee Name']}</b><br>
            Date: {row['Date'].date()}<br>
            Productivity: {round(row['Work productivity']*100,1)}%
            """
            folium.Marker(
                [row["Latitude"], row["Longitude"]],
                popup=popup_text,
                tooltip=row["Employee Name"]
            ).add_to(m)
        st_folium(m, width=1200, height=500)
    else:
        st.warning("No valid GPS data found for this employee.")
else:
    st.info("📌 Select a specific employee from the sidebar to view GPS map.")

st.markdown("---")

# =========================================================
# SECTION 8: AI PERFORMANCE SUGGESTION
# =========================================================

st.subheader("🤖 AI Performance Suggestion")

if avg_productivity >= 75:
    st.success(f"""
    ✅ **Excellent Performance! ({avg_productivity}%)**

    - Maintain current field activity levels
    - Increase TP visits slightly for further growth
    - Share best practices with lower performers
    - Consider for recognition or incentive programs
    """)
elif avg_productivity >= 50:
    st.warning(f"""
    ⚠️ **Average Performance ({avg_productivity}%)**

    - Reduce idle hours through better route planning
    - Increase outlet visit frequency daily
    - Review travel routes for efficiency
    - Set daily working targets per employee
    """)
else:
    st.error(f"""
    🚨 **Low Performance Detected ({avg_productivity}%)**

    - Minimize idle time immediately
    - Increase active working hours
    - Improve daily movement & route planning
    - Reduce unnecessary travel stops
    - Increase TP coverage targets
    - Monitor field activity with daily check-ins
    """)

st.markdown("---")

# =========================================================
# SECTION 9: DETAIL TABLE + DOWNLOAD
# =========================================================

st.subheader("📋 Detailed Data Table")

display_df = df.copy()
display_df["Date"] = display_df["Date"].dt.date
display_df["Work productivity"] = (
    display_df["Work productivity"] * 100).round(1)
display_df = display_df.rename(columns={"Work productivity": "Productivity %"})

st.dataframe(display_df, use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇ Download Filtered Report (CSV)",
    csv,
    "field_force_report.csv",
    "text/csv"
)
